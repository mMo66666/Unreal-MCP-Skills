# UE5 Level Design CN

A designer-oriented Codex skill for planning, building, reviewing, and validating Unreal Engine 5 levels through Unreal MCP and optional VibeUE tools.

## What It Covers

- Current-level auditing and safe editor workflows
- Player scale, routes, loops, bottlenecks, and POIs
- Terrain, water, roads, parcels, buildings, props, and vegetation
- PCG, Foliage, World Partition, and Data Layer considerations
- Asset Bounds, semantic scale, overlap, and duplicate checks
- Viewport review, PIE validation, streaming, and performance evidence
- A read-only Level Doctor report for large scene audits

## Requirements

- Unreal Engine 5.8 with Unreal MCP available in the editor
- Codex or another compatible MCP client
- VibeUE is optional and used only when its live toolsets are available

## Installation

Copy this repository into either a project-level or personal Codex skills directory:

```text
<project>/.codex/skills/ue5-level-design-cn
```

or:

```text
~/.codex/skills/ue5-level-design-cn
```

## Usage

Reference the skill in a Codex request:

```text
Use $ue5-level-design-cn to audit the currently open UE5 level and propose a safe iteration plan.
```

The skill communicates with designers in Chinese, performs Unreal MCP calls serially, and separates planning, diagnosis, implementation, and validation work.

## Repository Structure

```text
ue5-level-design-cn/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── brief-template.md
│   ├── level-doctor.md
│   ├── quality-gates.md
│   ├── tool-routing.md
│   └── workflow.md
└── scripts/
    └── level_doctor.py
```

## Validation

The bundled Level Doctor is read-only: it generates structured candidates for scale, AABB overlap, and duplicate review without modifying the level. Visual inspection, traces, and PIE remain required for final judgment.
