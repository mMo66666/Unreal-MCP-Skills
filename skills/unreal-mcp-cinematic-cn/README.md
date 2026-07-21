# UE5 Cinematic Shot Language

A designer-oriented Codex Skill for translating shot descriptions, storyboards, timed scripts, character beats, and camera intent into executable and reviewable Unreal Engine 5 Sequencer work.

The Skill does not replace the designer as director. It preserves the supplied story and shot intent while helping an AI agent complete the technical specification, operate Sequencer through Unreal MCP or VibeUE, validate the resulting structure, and report what still requires human playback review.

## What It Supports

- Level Sequence and Cine Camera creation or modification
- Camera Cut planning, binding, timing, and continuity checks
- Camera paths, composition, focal length, focus, and depth-of-field control
- Character animation timing and representative-pose inspection
- Crane, Rail, Transform, Look At, Rotation, and Camera Shake workflows
- Read-only scene reconnaissance before camera construction
- UE 5.8, Unreal MCP, VibeUE, and native UE Python fallback paths
- Structural readback, risk-frame screening, MRQ PNG diagnostics, and rework
- Fast single-shot tests, dynamic drafts, production passes, and finished-output checks

## Design Principles

- Preserve designer ownership of story, beats, shot count, and intended memorable images.
- Let the AI choose implementation details when they do not change creative intent.
- Use change-driven execution instead of rebuilding or validating unaffected tracks.
- Prefer the current client's native Unreal MCP tools over hand-built HTTP or SSE transport.
- Cache live schemas and batch repeated keyframe operations when supported.
- Keep camera motion, orientation, focus, and high-frequency organic motion editable.
- Never claim smooth motion or finished quality without continuous playback, recording, rendering, or equivalent temporal evidence.
- Avoid moving, deleting, rebuilding, or generating unrelated scene actors unless explicitly authorized.

## Installation

Clone the repository into a Codex skills directory:

```bash
git clone https://github.com/mMo66666/UE5_Cinematic_Skill.git ue5-cinematic-shot-language-cn
```

Typical personal installation path on Windows:

```text
C:\Users\Administrator\.codex\skills\ue5-cinematic-shot-language-cn
```

For a project-local installation, place it under:

```text
<UnrealProject>\.codex\skills\ue5-cinematic-shot-language-cn
```

The folder name should match the `name` field in `SKILL.md`.

## Example Request

```text
Use the ue5-cinematic-shot-language-cn Skill to create a 20-second production-level
Sequencer camera sequence in the currently open town scene.

Inspect the scene through MCP before writing. Reuse existing actors, do not rebuild
the scene, and do not move unrelated actors. Build six Camera Cuts that progress
from a peaceful town introduction to an emergency vehicle reveal. Report the Level
Sequence path, Camera Cut ranges, keyframe responsibilities, focus behavior, binding
status, and any remaining occlusion, clipping, exposure, UI, or motion-review risks.
```

## Execution Depths

The Skill supports five levels of execution:

1. Static storyboard
2. Fast single shot
3. Fast dynamic draft
4. Production pass
5. Finished-output check

The selected depth defines the minimum write and validation requirements. It does not impose a fixed creative template or a fixed tool order.

## Validation Boundary

Sequencer data and still frames can verify structure and the inspected compositions. They cannot, by themselves, prove motion smoothness, subjective pacing, performance quality, or final delivery quality.

When continuous visual evidence is unavailable, the Skill reports the verified structural level and clearly identifies what the designer still needs to review at normal playback speed.

## Repository Structure

```text
SKILL.md                     Core workflow and reference navigation
agents/openai.yaml           Skill metadata for Codex interfaces
references/                  Task-specific execution and validation guidance
scripts/mrq_png_diagnostics.py
                             Optional low-cost MRQ PNG diagnostic helper
```

Detailed references are loaded only when needed so the main Skill remains concise and does not unnecessarily constrain capable models.
