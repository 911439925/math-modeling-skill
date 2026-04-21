---
name: math-modeling
description: >
  Full-pipeline mathematical modeling agent for MCM/ICM competitions. Activates when
  the user mentions "math modeling", "mathematical modeling", "美赛", "国赛", "建模",
  "MCM", "ICM", or asks to solve a modeling competition problem. Also use when the user
  wants to analyze a problem, build a mathematical model, decompose it into subtasks,
  and solve each subtask with code execution. Covers the complete workflow from problem
  understanding to solution generation.
version: 0.1.0
---

# Mathematical Modeling Agent (MM-Skill)

A stage-by-stage mathematical modeling agent that simulates the expert modeling workflow for competition problems.

## Overview

This skill guides Claude Code through a structured 3-stage modeling pipeline:

1. **Stage 1 - Problem Analysis**: Deep analysis with Actor-Critic self-improvement
2. **Stage 2 - Modeling & Decomposition**: High-level modeling, task splitting, DAG scheduling
3. **Stage 3 - Task Solving**: Per-task HMML retrieval, formula generation, code execution

Each stage pauses for user review before proceeding.

## Activation

This skill activates when the user:
- Provides a mathematical modeling competition problem
- Mentions "美赛", "国赛", "建模", "MCM", "ICM"
- Asks to solve a modeling problem end-to-end
- Uses the `/math-model` command

## Prerequisites

Before starting, verify:
- Python 3.10+ is available (run `python --version`)
- Required libraries: numpy, pandas, scipy, matplotlib (install if missing)
- Working directory is writable

## Workflow

### Initialization

1. Create the workspace directory structure:
   ```bash
   mkdir -p mm-workspace/code mm-workspace/data mm-workspace/charts
   ```

2. Read and extract the problem:
   - If the user provides a file path (PDF, image, text), read it using the Read tool
   - If the user provides text directly, use it as the problem
   - Identify if there are attached dataset files
   - Save the raw problem to `mm-workspace/raw_problem.txt`

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

For each task:
- Solve it following the mm-solving skill instructions
- Present the task results to the user
- Ask: "任务 {id} 完成，是否继续下一个任务？"
- Wait for user confirmation

### Final Summary

After all tasks are complete:
- Summarize all task results
- List all generated files (code, data, charts)
- Provide a brief overall conclusion
- Ask if the user wants to proceed with report/paper generation (future feature)

## Error Recovery

- If any stage fails, save progress to the workspace JSON files
- The user can resume from the last completed stage
- If a task's code fails after 3 debug rounds, mark it as failed and continue with other tasks
- Never delete workspace files without user confirmation

## Key References

Load these reference files as needed:
- `references/hmml.md` - HMML knowledge base (load during Stage 3)
- `references/actor_critic.md` - Actor-Critic mechanism guide
- `references/dag_scheduler.md` - DAG scheduling strategy
- `references/code_templates.md` - Code template specification
