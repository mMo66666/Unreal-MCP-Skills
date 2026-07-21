"""UE5 MRQ PNG 诊断辅助。

在 UE Python 中调用 start_png_render；在 UE 外也可调用 verify_png_sequence
验证已经落盘的 PNG。脚本不负责镜头审美判断。
"""

from __future__ import annotations

from pathlib import Path
from collections import Counter
import re
import struct

try:
    import unreal
except ImportError:  # 允许在 UE 外验证 PNG 文件
    unreal = None


def _require_unreal():
    if unreal is None:
        raise RuntimeError("该操作必须在 Unreal Editor Python 环境中运行")


def _object_path(asset_path: str) -> str:
    """把 /Game/A/B 规范化为可用于 SoftObjectPath 的完整对象路径。"""
    _require_unreal()
    asset = unreal.load_asset(asset_path)
    if not asset:
        raise RuntimeError(f"资产不存在或无法加载: {asset_path}")
    return asset.get_path_name()


def mrq_state() -> dict:
    _require_unreal()
    subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    queue = subsystem.get_queue()
    return {
        "is_rendering": bool(subsystem.is_rendering()),
        "job_count": len(queue.get_jobs()),
        "active_executor": bool(subsystem.get_active_executor()),
    }


def start_png_render(
    sequence_path: str,
    map_path: str,
    output_directory: str,
    start_frame: int,
    end_frame: int,
    resolution=(640, 360),
    frame_step: int = 1,
    warm_up_frames: int = 2,
    job_name: str = "Codex_MRQ_PNG_Diagnostic",
    allow_overwrite: bool = False,
) -> dict:
    """向空 MRQ 队列提交一个左闭右开区间的低成本 PNG 诊断任务。"""
    _require_unreal()
    if end_frame <= start_frame:
        raise ValueError("end_frame 必须大于 start_frame")
    if frame_step < 1:
        raise ValueError("frame_step 必须为正整数")
    if warm_up_frames < 0:
        raise ValueError("warm_up_frames 不能小于 0")
    if resolution[0] < 1 or resolution[1] < 1:
        raise ValueError("resolution 必须为正整数")

    subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    if subsystem.is_rendering():
        raise RuntimeError("MRQ 正在渲染，未提交新任务")
    queue = subsystem.get_queue()
    if queue.get_jobs():
        raise RuntimeError("MRQ 队列非空；先确认所有权，不得静默覆盖现有 Job")

    output_folder = Path(output_directory)
    existing_png = sorted(str(path) for path in output_folder.glob("*.png")) if output_folder.is_dir() else []
    if existing_png and not allow_overwrite:
        raise RuntimeError("输出目录已包含 PNG；改用独立目录或显式设置 allow_overwrite=True")

    sequence_object_path = _object_path(sequence_path)
    map_object_path = _object_path(map_path)
    job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
    author = "Codex"
    comment = f"PNG diagnostic [{start_frame},{end_frame})"
    try:
        job.set_editor_property("job_name", job_name)
        job.set_editor_property("author", author)
        job.set_editor_property("comment", comment)
        job.set_editor_property("sequence", unreal.SoftObjectPath(sequence_object_path))
        job.set_editor_property("map", unreal.SoftObjectPath(map_object_path))

        config = job.get_configuration()
        output = config.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
        output.set_editor_property("output_directory", unreal.DirectoryPath(path=output_directory))
        output.set_editor_property("file_name_format", "{sequence_name}_{frame_number}")
        output.set_editor_property("output_resolution", unreal.IntPoint(*resolution))
        output.set_editor_property("use_custom_playback_range", True)
        output.set_editor_property("custom_start_frame", int(start_frame))
        output.set_editor_property("custom_end_frame", int(end_frame))
        output.set_editor_property("output_frame_step", int(frame_step))
        output.set_editor_property("zero_pad_frame_numbers", 4)
        output.set_editor_property("override_existing_output", bool(allow_overwrite))
        output.set_editor_property("flush_disk_writes_per_shot", True)

        config.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)
        config.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
        aa = config.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)
        aa.set_editor_property("spatial_sample_count", 1)
        aa.set_editor_property("temporal_sample_count", 1)
        aa.set_editor_property("engine_warm_up_count", int(warm_up_frames))
        aa.set_editor_property("render_warm_up_count", int(warm_up_frames))
        aa.set_editor_property("render_warm_up_frames", warm_up_frames > 0)

        executor = subsystem.render_queue_with_executor(unreal.MoviePipelinePIEExecutor)
        if not executor:
            raise RuntimeError("MRQ Executor 未创建，诊断任务未提交")
    except Exception as exc:
        cleanup_error = None
        if not subsystem.is_rendering():
            try:
                if job in queue.get_jobs():
                    queue.delete_job(job)
            except Exception as error:
                cleanup_error = error
        if cleanup_error is not None:
            raise RuntimeError(f"MRQ 提交失败，且本次诊断 Job 回滚失败: {cleanup_error}") from exc
        raise
    return {
        "submitted": bool(executor),
        "is_rendering_immediate": bool(subsystem.is_rendering()),
        "output_directory": output_directory,
        "range": [start_frame, end_frame],
        "frame_step": frame_step,
        "allow_overwrite": allow_overwrite,
        "cleanup_identity": {
            "job_name": job_name,
            "author": author,
            "comment": comment,
        },
        "note": "提交成功不等于落盘成功；等待异步结束后验证 PNG",
    }


def clear_diagnostic_job_if_idle(job_name: str, author: str, comment: str) -> int:
    """仅删除精确匹配本次诊断身份的单个空闲 Job。"""
    _require_unreal()
    if not job_name or not author or not comment:
        raise ValueError("清理诊断 Job 必须提供完整 cleanup_identity")
    subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    if subsystem.is_rendering():
        raise RuntimeError("MRQ 正在渲染，不能清理队列")
    queue = subsystem.get_queue()
    matches = [
        job
        for job in queue.get_jobs()
        if job.get_editor_property("job_name") == job_name
        and job.get_editor_property("author") == author
        and job.get_editor_property("comment") == comment
    ]
    if not matches:
        return 0
    if len(matches) != 1:
        raise RuntimeError("诊断 Job 身份不唯一，拒绝自动清理")
    queue.delete_job(matches[0])
    return 1


def _png_size(path: Path):
    with path.open("rb") as stream:
        if stream.read(8) != b"\x89PNG\r\n\x1a\n":
            return None
        length = struct.unpack(">I", stream.read(4))[0]
        chunk_type = stream.read(4)
        if chunk_type != b"IHDR" or length < 8:
            return None
        return struct.unpack(">II", stream.read(8))


def verify_png_sequence(
    output_directory: str,
    start_frame: int | None = None,
    end_frame: int | None = None,
    frame_step: int = 1,
) -> dict:
    """验证 PNG 文件、尺寸和预期窗口；end_frame 为右开边界。"""
    if frame_step < 1:
        raise ValueError("frame_step 必须为正整数")
    if (start_frame is None) != (end_frame is None):
        raise ValueError("start_frame 和 end_frame 必须同时提供或同时省略")
    if start_frame is not None and end_frame <= start_frame:
        raise ValueError("end_frame 必须大于 start_frame")
    folder = Path(output_directory)
    numbered = []
    for path in sorted(folder.glob("*.png")):
        match = re.search(r"_(\d+)$", path.stem)
        if match:
            numbered.append((int(match.group(1)), path))

    frames = [frame for frame, _ in numbered]
    duplicate_frames = sorted(frame for frame, count in Counter(frames).items() if count > 1)
    invalid = [str(path) for _, path in numbered if _png_size(path) is None]
    dimensions = sorted({size for _, path in numbered if (size := _png_size(path))})
    range_provided = start_frame is not None
    missing = []
    unexpected = []
    if range_provided:
        expected = set(range(start_frame, end_frame, frame_step))
        actual = set(frames)
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)

    directory_exists = folder.is_dir()
    files_valid = directory_exists and bool(numbered) and not duplicate_frames and not invalid
    dimensions_consistent = bool(numbered) and len(dimensions) == 1
    coverage_valid = not missing and not unexpected if range_provided else None
    evidence_valid = files_valid and dimensions_consistent and coverage_valid is True

    return {
        "directory_exists": directory_exists,
        "count": len(numbered),
        "frames": frames,
        "duplicate_frames": duplicate_frames,
        "missing_frames": missing,
        "unexpected_frames": unexpected,
        "invalid_png": invalid,
        "dimensions": dimensions,
        "files_valid": files_valid,
        "dimensions_consistent": dimensions_consistent,
        "range_provided": range_provided,
        "coverage_valid": coverage_valid,
        "evidence_valid": evidence_valid,
        "valid": evidence_valid,
    }
