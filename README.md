# MM-Skill: Mathematical Modeling Plugin for Claude Code

A Claude Code skill plugin for full-pipeline mathematical modeling, designed for MCM/ICM and similar competitions.

## Features

- **Problem Analysis**: Deep analysis with Actor-Critic self-improvement
- **Modeling & Decomposition**: High-level modeling solution, task splitting, DAG scheduling
- **Task Solving**: HMML method retrieval, formula generation, Python code execution
- **Semi-Automatic**: Pause at each stage for user review and modification

## Installation

Copy this directory to your Claude Code skills/plugins directory, or link it from your project's `.claude` settings.

## Usage

### Start the Pipeline

```
/math-model path/to/problem.pdf
```

Or simply describe your problem:

```
/math-model 2024年美赛C题：网球比赛中的动量
```

### Stages

| Stage | Skill | Description |
|-------|-------|-------------|
| 1 | mm-analysis | Problem analysis with Actor-Critic |
| 2 | mm-modeling | High-level modeling + task decomposition + DAG |
| 3 | mm-solving | Per-task: HMML retrieval → formulas → code → results |

Each stage pauses for your review before proceeding.

### Output Structure

```
mm-workspace/
├── 01_analysis.json          # Stage 1 output
├── 02_modeling.json          # Stage 2 output
├── 03_task_1.json ...        # Stage 3 per-task outputs
├── code/                     # Generated Python scripts
├── data/                     # Intermediate data files
└── charts/                   # Generated visualizations
```

## Requirements

- Python 3.10+
- numpy, pandas, scipy, matplotlib, seaborn

## Architecture

Inspired by [MM-Agent](https://arxiv.org/abs/2505.14148) (NeurIPS 2025), adapted for Claude Code's native capabilities:

| MM-Agent | MM-Skill |
|----------|----------|
| API calls per step | Claude Code is the LLM |
| subprocess execution | Bash tool native execution |
| Embedding retrieval | Claude Code semantic understanding |
| Single CLI run | Semi-automatic with stage pauses |

## License

CC BY-NC (based on MM-Agent)
