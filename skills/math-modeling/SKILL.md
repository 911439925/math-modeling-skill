---
name: math-modeling
description: >
  Universal mathematical modeling agent for all competitions. Activates when
  the user mentions "math modeling", "mathematical modeling", "美赛", "国赛", "建模",
  "MCM", "ICM", "MathorCup", or asks to solve a modeling competition problem.
  Also use when the user wants to analyze a problem, build a mathematical model,
  decompose it into subtasks, and solve each subtask with code execution.
  Covers the complete workflow from problem understanding to LaTeX paper generation.
version: 0.2.0
---

# Mathematical Modeling Agent (MM-Skill)

A stage-by-stage mathematical modeling agent for all competition types.

## Overview

This skill guides Claude Code through a structured 4-stage modeling pipeline:

1. **Stage 1 - Problem Analysis**: Deep analysis with Actor-Critic self-improvement
2. **Stage 2 - Modeling & Decomposition**: High-level modeling, task splitting, DAG scheduling
3. **Stage 3 - Task Solving**: Per-task HMML retrieval, formula generation, code execution
4. **Stage 4 - Paper Generation**: LaTeX source generation, compilation to PDF

Stage 1 and 2 pause for user review. Stage 3 runs automatically unless errors occur. Stage 4 pauses for final review.

## Activation

This skill activates when the user:
- Provides a mathematical modeling competition problem
- Mentions "美赛", "国赛", "建模", "MCM", "ICM", "MathorCup"
- Asks to solve a modeling problem end-to-end
- Uses the `/math-model` command

## Prerequisites

Before starting, verify and install dependencies:

1. Python 3.10+ (run `python --version`)
2. Install required libraries:
   ```bash
   pip install numpy pandas scipy matplotlib seaborn scikit-learn networkx sympy openpyxl statsmodels
   ```
3. TeX distribution for paper compilation (TeX Live or MiKTeX)
4. Working directory is writable

## Workflow

### Initialization

1. Create the workspace directory structure:
   ```bash
   mkdir -p mm-workspace/code mm-workspace/data mm-workspace/charts mm-workspace/05_paper/sections mm-workspace/05_paper/figures
   ```

2. Read and extract the problem:
   - If the user provides a file path (PDF, image, text), read it using the Read tool
   - If the user provides text directly, use it as the problem
   - Identify if there are attached dataset files
   - Save the raw problem to `mm-workspace/raw_problem.txt`

3. Detect competition type if user mentions it (affects paper template and language)

### Stage 1: Problem Analysis (invoke mm-analysis skill)

After initialization, invoke the `mm-analysis` skill to perform deep problem analysis.

**Input**: Problem text + dataset files (if any)
**Output**: `mm-workspace/01_analysis.json`

After Stage 1 completes:
- Present the analysis summary to the user
- Ask: "问题分析完成，是否需要修改？确认后进入建模阶段。"
- Wait for user confirmation before proceeding

### Stage 2: Modeling & Decomposition (invoke mm-modeling skill)

After user confirms Stage 1, invoke the `mm-modeling` skill.

**Input**: `mm-workspace/01_analysis.json`
**Output**: `mm-workspace/02_modeling.json`

After Stage 2 completes:
- Present the modeling solution and task decomposition to the user
- Ask: "建模方案和任务分解完成，是否需要修改？确认后开始逐任务求解。"
- Wait for user confirmation before proceeding

### Stage 3: Task Solving (invoke mm-solving skill)

After user confirms Stage 2, invoke the `mm-solving` skill for each task in DAG order.

**Input**: `mm-workspace/01_analysis.json` + `mm-workspace/02_modeling.json`
**Output**: `mm-workspace/03_task_{id}.json` for each task

Task solving runs **automatically** through all tasks:
- Solve each task following the mm-solving skill instructions
- Display task results as they complete
- Only pause if a task fails or user explicitly interrupts

### Stage 4: Paper Generation (invoke mm-writing skill)

After all tasks complete, invoke the `mm-writing` skill for LaTeX paper generation.

**Input**: All workspace JSON files + code + charts
**Output**: `mm-workspace/05_paper/main.tex` → compiled `mm-workspace/05_paper/main.pdf`

See `mm-writing` skill for details.

### Final Summary

After paper generation:
- Summarize all task results and paper output
- List all generated files (code, data, charts, paper)
- Provide the PDF file path

## Error Recovery

- If any stage fails, save progress to the workspace JSON files
- The user can resume from the last completed stage
- If a task's code fails after 3 debug rounds, mark it as failed and continue with other tasks
- Never delete workspace files without user confirmation

## Key References

Load these reference files as needed:
- `references/hmml_index.md` - HMML method index (load first during Stage 3)
- `references/hmml_*.md` - HMML domain files (load relevant domains only)
- `references/actor_critic.md` - Actor-Critic mechanism guide
- `references/dag_scheduler.md` - DAG scheduling strategy
- `references/code_templates.md` - Code template specification
- `references/abstract_guide.md` - Abstract generation guide
