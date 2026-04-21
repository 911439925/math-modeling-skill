# MM-Skill: Universal Mathematical Modeling Plugin for Claude Code

A Claude Code skill plugin for full-pipeline mathematical modeling, designed for **all major math modeling competitions**.

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
/plugin update math-modeling@mm-skill-market
```

Git clone users:
```bash
cd ~/.claude/skills/math-modeling-plugin && git pull
```

## Features

- **Problem Analysis**: Deep analysis with Actor-Critic self-improvement (independent Critic subagent)
- **Modeling & Decomposition**: High-level modeling solution, task splitting, DAG scheduling
- **Task Solving**: HMML method retrieval, formula generation, Python code execution, result verification
- **Global Quality Review**: Independent 5-dimension review with iterative rework (up to 3 rounds)
- **Sensitivity Analysis**: Systematic sensitivity and robustness testing
- **Paper Generation**: LaTeX source generation with competition-specific templates → PDF
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
Initialization → Stage 1 → Stage 2 → Stage 3 → Stage 3.5 → [iterate?] → Stage 4 → Final
                  ↓          ↓          ↓(auto)    ↓(subagent)              ↓
               [review]   [review]   per-task   global review           LaTeX→PDF
               [pause]    [pause]    +verify     +rework loop            [pause]
```

| Stage | Skill | Description | Pause? |
|-------|-------|-------------|--------|
| Init | math-model-command | Workspace init, git init, problem extraction | No |
| 1 | mm-analysis | Problem analysis with Actor-Critic (independent Critic) | Yes |
| 2 | mm-modeling | Modeling + task decomposition + DAG | Yes |
| 3 | mm-solving | Per-task: HMML → formulas → code → verify (auto) | No |
| 3.5 | mm-review | Global quality review (independent subagent, max 3 iterations) | On rework |
| 4 | mm-writing | LaTeX paper generation → PDF | Yes |

### Global Constraints

- Max 2 concurrent subagents at any time
- Git commit after every stage + task
- Iteration tags for version tracking

### Output Structure

```
mm-workspace/
├── .git/                     # Git version history
├── 01_analysis.json          # Stage 1 output
├── 02_modeling.json          # Stage 2 output
├── 03_task_1.json ...        # Stage 3 per-task outputs (with verification)
├── 03.5_review.json          # Stage 3.5 global review
├── 04_abstract.json          # Generated abstract
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

References:
- [MM-Agent](https://arxiv.org/abs/2505.14148) (NeurIPS 2025) — core pipeline design reference

| Concept | Implementation |
|---------|---------------|
| Pipeline orchestration | Claude Code as the LLM, stage-based SKILL files |
| Method retrieval | HMML knowledge base with domain-level on-demand loading |
| Code execution | Bash tool native execution |
| Self-improvement | Actor-Critic with independent Critic subagent + adaptive rounds |
| Quality assurance | Per-task verification + global review with iterative rework |
| Version management | Git per-stage commits + iteration tags |
| Paper generation | LaTeX templates (MCM/CUMCM/generic) → PDF compilation |

## License

CC BY-NC
