# MM-Skill: Universal Mathematical Modeling Plugin for Claude Code

[中文文档](README_CN.md)

A Claude Code skill plugin for full-pipeline mathematical modeling, designed for **all major math modeling competitions**.

> **Current version: v0.4.4** — Pipeline state machine, schema enforcement, automated validation scripts.

## Supported Competitions

| Competition | Abbr | Duration | Notes |
|-------------|------|----------|-------|
| Mathematical Contest in Modeling | MCM | 4 days | English paper |
| Interdisciplinary Contest in Modeling | ICM | 4 days | English paper |
| 全国大学生数学建模竞赛 | CUMCM | 3 days | Chinese paper |
| MathorCup 高校数学建模挑战赛 | MathorCup | 4 days | Chinese paper |
| 深圳杯数学建模挑战赛 | SZ Cup | ~2 weeks | Chinese paper |
| 其他建模比赛 | — | — | LaTeX templates extensible |

## Installation

### Option 1: Claude Code Marketplace (Recommended)

```bash
# Add the marketplace
/plugin marketplace add 911439925/math-modeling-skill

# Install the plugin
/plugin install math-modeling@mm-skill-market
```

Private repo: set `GITHUB_TOKEN` env var first:
```bash
export GITHUB_TOKEN=ghp_your_token_here
```

### Option 2: Git clone

```bash
# Clone to Claude Code skills directory
git clone https://github.com/911439925/math-modeling-skill.git ~/.claude/skills/math-modeling-plugin

# Windows PowerShell
git clone https://github.com/911439925/math-modeling-skill.git "$env:USERPROFILE\.claude\skills\math-modeling-plugin"
```

### Updating

Marketplace users:
```bash
/plugin marketplace update mm-skill-market
/plugin install math-modeling@mm-skill-market
```

Git clone users:
```bash
cd ~/.claude/skills/math-modeling-plugin && git pull
```

## Features

- **Problem Analysis**: Deep analysis with Actor-Critic self-improvement (independent Critic subagent)
- **Modeling & Decomposition**: High-level modeling solution, task splitting (3-6 subtasks), DAG scheduling
- **Task Solving**: HMML method retrieval (98 methods, 5 domains), formula generation, Python code execution, result verification
- **Global Quality Review**: Independent 6-dimension review with iterative rework (up to 3 rounds, 80-point threshold)
- **Sensitivity Analysis**: Systematic sensitivity and robustness testing (REQUIRED/RECOMMENDED/OPTIONAL priority)
- **Paper Generation**: LaTeX source generation with competition-specific templates (MCM/CUMCM/generic) → PDF
- **Pipeline State Machine**: `pipeline_state.json` enforces stage transitions — no stage can be skipped
- **Schema Validation**: Automated task output validation (`validate_task_output.py`) with backfill
- **Cross-Task Consistency**: Automated metric conflict and value chain checks (`cross_task_consistency.py`)
- **Git Versioning**: Automatic workspace versioning with per-stage commits and iteration tags

## Usage

### Start the Pipeline

```
/math-model path/to/problem.pdf
```

Or simply describe your problem:

```
/math-model 2026年美赛C题
```

### Pipeline Stages

```
Init → Stage 1 → Stage 2 → Stage 3 → Stage 3.5 → [iterate?] → Stage 4 → Final
         ↓          ↓          ↓(auto)    ↓(mandatory)            ↓
      [review]   [review]   per-task    global review          LaTeX→PDF
      [pause]    [pause]    +verify     +rework loop            [pause]
```

| Stage | Skill | Description | Pause? |
|-------|-------|-------------|--------|
| Init | math-model-command | Workspace init, git init, problem extraction, pipeline state init | No |
| 1 | mm-analysis | Problem analysis with Actor-Critic (independent Critic, 75-point threshold) | Yes |
| 2 | mm-modeling | Modeling + task decomposition + DAG (75-point threshold) | Yes |
| 3 | mm-solving | Per-task: HMML → formulas → code → schema validate → verify | No |
| 3.5 | mm-review | Global quality review (independent subagent, 80-point threshold, max 3 iterations) | On rework |
| 4 | mm-writing | LaTeX paper generation → PDF (requires Stage 3.5 passed) | Yes |

### Quality Gates

| Gate | Mechanism | Threshold |
|------|-----------|-----------|
| Stage 1 Actor-Critic | Independent Critic subagent scores the analysis | 75/100 |
| Stage 2 Actor-Critic | Independent Critic subagent scores the modeling | 75/100 |
| Per-task verification | Independent verification subagent checks each task result | Pass/Fail |
| Schema validation | `validate_task_output.py` checks required JSON fields | All required fields present |
| Cross-task consistency | `cross_task_consistency.py` checks metric conflicts + value chains | No conflicts |
| Global review | Independent review subagent, 6 dimensions, iterative rework | 80/100 |
| Stage 4 precondition | `pipeline_state.json` must show `stage_3_5_passed: true` | Hard gate |

### Output Structure

```
mm-workspace/
├── .git/                     # Git version history
├── pipeline_state.json       # Pipeline state machine (v0.4.4)
├── 01_analysis.json          # Stage 1 output
├── 02_modeling.json          # Stage 2 output (with DAG)
├── 03_task_1.json ...        # Stage 3 per-task outputs (with verification)
├── 03.5_review.json          # Stage 3.5 global review
├── 05_paper/                 # Stage 4 LaTeX paper
│   ├── main.tex              # Main LaTeX source
│   ├── main.pdf              # Compiled PDF
│   ├── sections/             # Paper sections
│   └── figures/              # Figures
├── code/                     # Generated Python scripts
├── data/                     # Intermediate data files
└── charts/                   # Generated visualizations
```

## Requirements

- Python 3.10+
- numpy, pandas, scipy, matplotlib, seaborn, scikit-learn, networkx, sympy, openpyxl, statsmodels
- TeX Live or MiKTeX (for paper compilation)
- Claude Code (Claude Opus 4.6+ recommended)

## Architecture

```
plugins/math-modeling/
├── .claude-plugin/plugin.json     # Plugin metadata
├── scripts/                       # Automation scripts
│   ├── validate_task_output.py    # Task JSON schema validation
│   └── cross_task_consistency.py  # Cross-task consistency checks
├── skills/
│   ├── math-modeling/             # Main orchestrator + references
│   │   ├── SKILL.md               # Pipeline definition, state machine, stage guards
│   │   └── references/            # HMML index, Actor-Critic guide, templates, etc.
│   ├── math-model-command/        # /math-model entry point
│   ├── mm-analysis/               # Stage 1: Problem analysis
│   ├── mm-modeling/               # Stage 2: Modeling & decomposition
│   ├── mm-solving/                # Stage 3: Task solving (subagent dispatch)
│   ├── mm-review/                 # Stage 3.5: Global quality review
│   └── mm-writing/                # Stage 4: Paper generation
```

### Key Design Decisions

| Concept | Implementation |
|---------|---------------|
| Pipeline enforcement | `pipeline_state.json` state machine with stage transition guards |
| Method retrieval | HMML knowledge base (98 methods, 5 domains) with on-demand loading |
| Self-improvement | Actor-Critic with independent Critic subagent + adaptive 1-3 rounds |
| Quality assurance | Per-task verification subagent + schema validation + global review |
| Cross-task integrity | `cross_task_consistency.py` + `known_issues` propagation via dispatch prompts |
| Error recovery | Fix verification loop (max 1 re-attempt) + `_schema_incomplete` fallback |
| Paper generation | LaTeX templates (MCM/CUMCM/generic) → PDF compilation |

### References

- [MM-Agent](https://arxiv.org/abs/2505.14148) (NeurIPS 2025) — core pipeline design reference

## Changelog

### v0.4.4
- Pipeline state machine (`pipeline_state.json`) with stage transition guards
- Task output schema validation script (`validate_task_output.py`)
- Cross-task consistency check script (`cross_task_consistency.py`)
- Stage 3.5 hard precondition in mm-writing (4-point verification)
- Verification results standardized (embedded in task JSON)
- Known issues propagation between subagents via dispatch prompts
- Git commit/tag enforcement policy
- Parallel dispatch fallback (sequential acceptable)
- Sensitivity analysis test priority (REQUIRED/RECOMMENDED/OPTIONAL)
- Fix verification loop (max 1 re-attempt per issue type)

### v0.4.3
- Per-task verification gate enforcement
- Git operations removed from subagents (main agent only)

### v0.4.2
- Methodological rigor enhancements from MCM C practice

### v0.4.1
- Actor-Critic percent-based scoring system

### v0.4.0
- Subagent dispatch, independent verification, chart review, mandatory Stage 3.5

## License

CC BY-NC
