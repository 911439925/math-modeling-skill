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

## Features

- **Problem Analysis**: Deep analysis with Actor-Critic self-improvement
- **Modeling & Decomposition**: High-level modeling solution, task splitting, DAG scheduling
- **Task Solving**: HMML method retrieval, formula generation, Python code execution
- **Sensitivity Analysis**: Systematic sensitivity and robustness testing
- **Paper Generation**: LaTeX source generation with competition-specific templates → PDF
- **Semi-Automatic**: Configurable pause points for user review

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
| 0 | math-model-command | Entry point, workspace init |
| 1 | mm-analysis | Problem analysis with Actor-Critic |
| 2 | mm-modeling | High-level modeling + task decomposition + DAG |
| 3 | mm-solving | Per-task: HMML retrieval → formulas → code → results |
| 4 | mm-writing | LaTeX paper generation → PDF |

Stage 1-2 pauses for user review. Stage 3 runs automatically unless errors occur.

### Output Structure

```
mm-workspace/
├── 01_analysis.json          # Stage 1 output
├── 02_modeling.json          # Stage 2 output
├── 03_task_1.json ...        # Stage 3 per-task outputs
├── 04_abstract.json          # Generated abstract
├── 05_paper/                 # Stage 4 LaTeX paper
│   ├── main.tex              # Main LaTeX source
│   ├── sections/             # Paper sections
│   ├── figures/              # Figures (symlinked from charts/)
│   └── main.pdf              # Compiled PDF
├── code/                     # Generated Python scripts
├── data/                     # Intermediate data files
└── charts/                   # Generated visualizations
```

## Requirements

- Python 3.10+
- numpy, pandas, scipy, matplotlib, seaborn, scikit-learn, networkx, sympy, openpyxl, statsmodels
- TeX Live or MiKTeX (for paper compilation)

## Architecture

References:
- [MM-Agent](https://arxiv.org/abs/2505.14148) (NeurIPS 2025) — core pipeline design reference

| Concept | Implementation |
|---------|---------------|
| Pipeline orchestration | Claude Code as the LLM, stage-based SKILL files |
| Method retrieval | HMML knowledge base with domain-level on-demand loading |
| Code execution | Bash tool native execution |
| Self-improvement | Actor-Critic mechanism with adaptive rounds |
| Paper generation | LaTeX templates → PDF compilation |

## License

CC BY-NC
