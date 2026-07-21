import unreal

import datetime
import json
import math
import os
import re
import statistics


REPORT_VERSION = "0.1"
MAX_OVERLAP_RESULTS = 300
MIN_OVERLAP_DEPTH_CM = 1.0

IGNORE_TOKENS = (
    "ground", "road", "landscape", "water", "sky", "fog", "light",
    "volume", "navmesh", "spline", "postprocess", "reflectioncapture",
    "cloud", "volumetriccloud", "atmosphere", "skyatmosphere",
)

CATEGORY_TOKENS = {
    "small_prop": (
        "ricecooker", "cooker", "kettle", "toaster",
        "microwave", "teapot", "pot", "pan", "cup", "mug", "plate",
        "bowl", "bottle", "book", "phone", "clock", "radio", "bin",
        "trashcan", "rubbishbin",
    ),
    "furniture": (
        "chair", "table", "sofa", "couch", "bed", "cabinet", "shelf",
        "bench", "desk", "stool", "wardrobe", "dresser",
    ),
    "vehicle": ("vehicle", "car", "truck", "bus", "van", "tractor"),
    "vegetation": ("tree", "bush", "shrub", "plant", "grass", "flower"),
    "module": (
        "module", "wall", "floor", "roof", "ceiling", "corner",
        "doorframe", "windowframe", "pillar", "column", "trim",
    ),
    "building": (
        "building", "house", "shop", "church", "tower", "barn",
        "warehouse", "apartment", "factory", "garage",
    ),
}


def _round(value, digits=3):
    return round(float(value), digits)


def _vector(value):
    return {"x": _round(value.x), "y": _round(value.y), "z": _round(value.z)}


def _rotator(value):
    return {
        "pitch": _round(value.pitch),
        "yaw": _round(value.yaw),
        "roll": _round(value.roll),
    }


def _safe_label(actor):
    try:
        return actor.get_actor_label()
    except Exception:
        return actor.get_name()


def _static_mesh_paths(actor):
    paths = []
    try:
        components = actor.get_components_by_class(unreal.StaticMeshComponent)
    except Exception:
        return paths
    for component in components:
        try:
            mesh = component.get_editor_property("static_mesh")
            if mesh:
                paths.append(mesh.get_path_name())
        except Exception:
            continue
    return sorted(set(paths))


def _name_words(source_names):
    words = set()
    for source_name in source_names:
        snake_name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", source_name)
        name_words = [word for word in re.split(r"[^A-Za-z0-9]+", snake_name.lower()) if word]
        words.update(name_words)
        if name_words:
            words.add("".join(name_words))
    return words


def _classify(label, mesh_paths):
    asset_names = [path.rsplit("/", 1)[-1] for path in mesh_paths]
    label_words = _name_words([label])
    asset_words = _name_words(asset_names)
    if any(token in label_words or token in asset_words for token in IGNORE_TOKENS):
        return "ignored"
    words = asset_words if asset_words else label_words
    for category, tokens in CATEGORY_TOKENS.items():
        if any(token in words for token in tokens):
            return category
    return "unknown"


def _collect_actor(actor):
    label = _safe_label(actor)
    mesh_paths = _static_mesh_paths(actor)
    origin, extent = actor.get_actor_bounds(False, False)
    dimensions = {
        "x": max(0.0, float(extent.x) * 2.0),
        "y": max(0.0, float(extent.y) * 2.0),
        "z": max(0.0, float(extent.z) * 2.0),
    }
    location = actor.get_actor_location()
    rotation = actor.get_actor_rotation()
    scale = actor.get_actor_scale3d()
    bounds_min = {
        "x": float(origin.x - extent.x),
        "y": float(origin.y - extent.y),
        "z": float(origin.z - extent.z),
    }
    bounds_max = {
        "x": float(origin.x + extent.x),
        "y": float(origin.y + extent.y),
        "z": float(origin.z + extent.z),
    }
    volume = dimensions["x"] * dimensions["y"] * dimensions["z"]
    longest = max(dimensions.values())
    shortest = min(dimensions.values())
    return {
        "label": label,
        "actor_path": actor.get_path_name(),
        "class": actor.get_class().get_name(),
        "mesh_paths": mesh_paths,
        "category": _classify(label, mesh_paths),
        "location": _vector(location),
        "rotation": _rotator(rotation),
        "scale": _vector(scale),
        "bounds_origin": _vector(origin),
        "bounds_extent": _vector(extent),
        "bounds_min": {key: _round(value) for key, value in bounds_min.items()},
        "bounds_max": {key: _round(value) for key, value in bounds_max.items()},
        "dimensions_cm": {key: _round(value) for key, value in dimensions.items()},
        "longest_axis_cm": _round(longest),
        "shortest_axis_cm": _round(shortest),
        "bounds_volume_cm3": _round(volume),
        "has_valid_bounds": longest > 0.01,
    }


def _category_stats(records):
    stats = {}
    categories = sorted(set(item["category"] for item in records))
    for category in categories:
        items = [item for item in records if item["category"] == category and item["has_valid_bounds"]]
        lengths = [item["longest_axis_cm"] for item in items]
        heights = [item["dimensions_cm"]["z"] for item in items]
        stats[category] = {
            "count": len(items),
            "median_longest_axis_cm": _round(statistics.median(lengths)) if lengths else 0.0,
            "median_height_cm": _round(statistics.median(heights)) if heights else 0.0,
        }
    return stats


def _semantic_scale_candidates(records, stats):
    issues = []
    furniture_median = stats.get("furniture", {}).get("median_longest_axis_cm", 0.0)
    for item in records:
        if not item["has_valid_bounds"] or item["category"] in ("ignored", "unknown"):
            continue
        scale_values = [item["scale"][axis] for axis in ("x", "y", "z")]
        abs_scale = [abs(value) for value in scale_values]
        non_zero = [value for value in abs_scale if value > 0.0001]
        if any(value < 0.0 for value in scale_values):
            issues.append(_issue("P1_CANDIDATE", "negative_scale", item, "存在负缩放，需复核朝向、碰撞和法线。"))
        if non_zero and max(non_zero) / min(non_zero) >= 3.0:
            issues.append(_issue("P1_CANDIDATE", "non_uniform_scale", item, "非均匀缩放超过 3 倍，需复核比例与材质拉伸。"))
        if item["category"] == "small_prop" and furniture_median > 0.0:
            if item["longest_axis_cm"] >= furniture_median * 0.9:
                issues.append(_issue(
                    "P0_CANDIDATE",
                    "semantic_scale_inversion",
                    item,
                    "小型道具最长轴接近或超过家具中位尺寸，可能出现语义尺度倒挂。",
                    {"furniture_median_longest_axis_cm": furniture_median},
                ))

    for category, category_stat in stats.items():
        if category in ("ignored", "unknown") or category_stat["count"] < 4:
            continue
        median_size = category_stat["median_longest_axis_cm"]
        if median_size <= 0.0:
            continue
        for item in records:
            if item["category"] != category or not item["has_valid_bounds"]:
                continue
            ratio = item["longest_axis_cm"] / median_size
            if ratio >= 3.0 or ratio <= (1.0 / 3.0):
                issues.append(_issue(
                    "P1_CANDIDATE",
                    "category_size_outlier",
                    item,
                    "同类别尺寸偏离中位值超过 3 倍，需结合资产语义复核。",
                    {"category_median_longest_axis_cm": median_size, "ratio": _round(ratio)},
                ))
    return issues


def _issue(severity, issue_type, item, reason, evidence=None):
    return {
        "severity": severity,
        "type": issue_type,
        "actor": item["label"],
        "actor_path": item["actor_path"],
        "category": item["category"],
        "dimensions_cm": item["dimensions_cm"],
        "reason": reason,
        "evidence": evidence or {},
    }


def _overlap_depth(a, b):
    return {
        axis: min(a["bounds_max"][axis], b["bounds_max"][axis])
        - max(a["bounds_min"][axis], b["bounds_min"][axis])
        for axis in ("x", "y", "z")
    }


def _overlap_candidates(records):
    candidates = [
        item for item in records
        if item["has_valid_bounds"]
        and item["category"] != "ignored"
        and item["bounds_volume_cm3"] > 1000.0
        and item["shortest_axis_cm"] > 1.0
    ]
    candidates.sort(key=lambda item: item["bounds_min"]["x"])
    issues = []
    total = 0
    pair_checks = 0
    for index, first in enumerate(candidates):
        for second in candidates[index + 1:]:
            if second["bounds_min"]["x"] >= first["bounds_max"]["x"]:
                break
            pair_checks += 1
            depth = _overlap_depth(first, second)
            if min(depth.values()) <= MIN_OVERLAP_DEPTH_CM:
                continue
            overlap_volume = depth["x"] * depth["y"] * depth["z"]
            smaller_volume = min(first["bounds_volume_cm3"], second["bounds_volume_cm3"])
            if smaller_volume <= 0.0:
                continue
            ratio = overlap_volume / smaller_volume
            if ratio < 0.002:
                continue
            total += 1
            categories = {first["category"], second["category"]}
            if categories == {"building"}:
                severity = "P0_CANDIDATE"
                reason = "整栋建筑 AABB 明显重叠，需确认是否为非设计性穿插。"
            elif "module" in categories:
                severity = "REVIEW_MODULE_SEAM"
                reason = "模块接缝 AABB 重叠，需检查收口、可见穿模、Z-fighting 与碰撞。"
            else:
                severity = "P1_CANDIDATE"
                reason = "对象 AABB 重叠；AABB 不代表真实网格相交，必须局部视图复核。"
            if len(issues) < MAX_OVERLAP_RESULTS:
                issues.append({
                    "severity": severity,
                    "type": "aabb_overlap",
                    "actor_a": first["label"],
                    "actor_a_path": first["actor_path"],
                    "category_a": first["category"],
                    "actor_b": second["label"],
                    "actor_b_path": second["actor_path"],
                    "category_b": second["category"],
                    "overlap_depth_cm": {key: _round(value) for key, value in depth.items()},
                    "overlap_to_smaller_bounds_ratio": _round(ratio, 5),
                    "reason": reason,
                })
    return issues, total, pair_checks


def _duplicate_candidates(records):
    groups = {}
    for item in records:
        if not item["mesh_paths"] or item["category"] == "ignored":
            continue
        key = (
            tuple(item["mesh_paths"]),
            round(item["location"]["x"], 1),
            round(item["location"]["y"], 1),
            round(item["location"]["z"], 1),
        )
        groups.setdefault(key, []).append(item)
    issues = []
    for items in groups.values():
        if len(items) < 2:
            continue
        issues.append({
            "severity": "P0_CANDIDATE",
            "type": "possible_duplicate",
            "actors": [item["label"] for item in items],
            "actor_paths": [item["actor_path"] for item in items],
            "mesh_paths": items[0]["mesh_paths"],
            "location": items[0]["location"],
            "reason": "相同网格位于近似相同位置，可能是重复生成；旋转与用途仍需复核。",
        })
    return issues


def _severity_counts(issue_groups):
    counts = {}
    for group in issue_groups:
        for issue in group:
            severity = issue["severity"]
            counts[severity] = counts.get(severity, 0) + 1
    return counts


def run_level_doctor():
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if not actor_subsystem:
        raise RuntimeError("无法获取 EditorActorSubsystem")
    actors = list(actor_subsystem.get_all_level_actors())
    records = []
    failures = []
    for actor in actors:
        try:
            records.append(_collect_actor(actor))
        except Exception as exc:
            failures.append({"actor": _safe_label(actor), "error": str(exc)})

    world_path = "unknown_world"
    try:
        editor_world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
        if editor_world:
            world_path = editor_world.get_path_name()
    except Exception:
        if actors:
            world_path = actors[0].get_world().get_path_name()

    stats = _category_stats(records)
    semantic_issues = _semantic_scale_candidates(records, stats)
    overlap_issues, overlap_total, pair_checks = _overlap_candidates(records)
    duplicate_issues = _duplicate_candidates(records)
    severity_counts = _severity_counts([semantic_issues, overlap_issues, duplicate_issues])

    report = {
        "report_version": REPORT_VERSION,
        "generated_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "world": world_path,
        "units": "Unreal centimeters",
        "summary": {
            "level_actor_count": len(actors),
            "audited_actor_count": len(records),
            "actor_read_failures": len(failures),
            "valid_bounds_count": sum(1 for item in records if item["has_valid_bounds"]),
            "category_counts": {key: value["count"] for key, value in stats.items()},
            "semantic_scale_candidates": len(semantic_issues),
            "aabb_overlap_candidates_total": overlap_total,
            "aabb_overlap_candidates_saved": len(overlap_issues),
            "aabb_pair_checks": pair_checks,
            "possible_duplicates": len(duplicate_issues),
            "severity_counts": severity_counts,
        },
        "category_stats": stats,
        "issues": {
            "semantic_scale": semantic_issues,
            "aabb_overlaps": overlap_issues,
            "possible_duplicates": duplicate_issues,
        },
        "actor_inventory": records,
        "actor_read_failures": failures,
        "manual_checks_required": [
            "地表射线、Pivot 与真实接触面",
            "模块接缝收口、可见穿模、Z-fighting 与碰撞",
            "纹理尺度、UV 拉伸、接缝和平铺周期",
            "道具簇、负空间与人物高度可读带",
            "玩家视角截图、PIE、导航、触发、流送与性能",
        ],
        "limitations": [
            "语义分类仅根据 Actor/网格名称关键字生成候选，不是最终结论。",
            "AABB 会把空心建筑内部物体计为重叠，必须用局部视图和真实形状复核。",
            "脚本不修改关卡，不执行自动缩放、移动、删除或保存资产。",
        ],
    }

    saved_dir = os.path.abspath(unreal.Paths.project_saved_dir())
    report_dir = os.path.join(saved_dir, "LevelDoctor")
    os.makedirs(report_dir, exist_ok=True)
    world_name = re.sub(r"[^A-Za-z0-9_-]+", "_", world_path.rsplit("/", 1)[-1]) or "World"
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(report_dir, f"{world_name}_{timestamp}.json")
    with open(report_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    unreal.log(f"LEVEL_DOCTOR_REPORT={report_path}")
    unreal.log(f"LEVEL_DOCTOR_WORLD={world_path}")
    unreal.log(f"LEVEL_DOCTOR_ACTORS={len(records)}")
    unreal.log(f"LEVEL_DOCTOR_SEMANTIC_CANDIDATES={len(semantic_issues)}")
    unreal.log(f"LEVEL_DOCTOR_OVERLAP_CANDIDATES={overlap_total}")
    unreal.log(f"LEVEL_DOCTOR_DUPLICATE_CANDIDATES={len(duplicate_issues)}")
    return report_path, report


LEVEL_DOCTOR_REPORT_PATH, LEVEL_DOCTOR_REPORT = run_level_doctor()
