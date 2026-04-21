---
name: math-modeling
description: >
  Universal mathematical modeling agent for all competitions. Activates when
  the user mentions "math modeling", "mathematical modeling", "美赛", "国赛", "建模",
  "MCM", "ICM", "MathorCup", or asks to solve a modeling competition problem.
  Also use when the user wants to analyze a problem, build a mathematical model,
  decompose it into subtasks, and solve each subtask with code execution.
  Covers the complete workflow from problem understanding to LaTeX paper generation.
version: 0.3.0
---

# Mathematical Modeling Agent (MM-Skill)

A stage-by-stage mathematical modeling agent for all competition types.

## Overview

This skill guides Claude Code through a structured pipeline with global iteration:

1. **Stage 1 - Problem Analysis**: Deep analysis with Actor-Critic self-improvement
2. **Stage 2 - Modeling & Decomposition**: High-level modeling, task splitting, DAG scheduling
3. **Stage 3 - Task Solving**: Per-task HMML retrieval, formula generation, code execution
4. **Stage 3.5 - Global Review**: Independent quality review of all outputs (iterative)
5. **Stage 4 - Paper Generation**: LaTeX source generation, compilation to PDF

Stage 1 and 2 pause for user review. Stage 3 runs automatically unless errors occur. Stage 3.5 performs global quality review with up to 3 iterations. Stage 4 pauses for final review.

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

## Global Constraints

- **Max concurrent subagents**: 2. This includes Critic subagents (improvement A) and task-solving subagents. Never dispatch more than 2 Agent tool calls simultaneously. Batch parallel tasks into groups of 2 maximum.

### Initialization

1. Create the workspace directory structure:
   ```bash
   mkdir -p mm-workspace/code mm-workspace/data mm-workspace/charts mm-workspace/05_paper/sections mm-workspace/05_paper/figures
   ```

2. Initialize git version management:
   ```bash
   cd mm-workspace && git init
   ```
   Create `.gitignore` in mm-workspace:
   ```
   __pycache__/
   *.pyc
   .ipynb_checkpoints/
   *.aux
   *.log
   *.out
   *.bbl
   *.blg
   *.fls
   *.fdb_latexmk
   *.synctex.gz
   ```
   Then `git add -A && git commit -m "init: workspace initialized"`

3. Read and extract the problem:
   - If the user provides a file path (PDF, image, text), read it using the Read tool
   - If the user provides text directly, use it as the problem
   - Identify if there are attached dataset files
   - Save the raw problem to `mm-workspace/raw_problem.txt`

4. Detect competition type if user mentions it (affects paper template and language)

### Git Commit Protocol

After each stage or significant milestone, commit workspace state:

| 时机 | commit message |
|------|---------------|
| Stage 1 完成后 | `feat(s1): problem analysis complete` |
| Stage 2 完成后 | `feat(s2): modeling and decomposition complete` |
| Stage 3 每个任务完成后 | `feat(s3): task {id} solved` |
| Stage 3 全部完成（每轮迭代） | `feat(s3): all tasks solved - iteration {N}` |
| 全局审查通过后 | `git tag review-pass-v{N}` |
| Stage 4 完成后 | `feat(s4): paper generated` |
| 最终定稿 | `git tag final-v{N}` |

Commit command: `cd mm-workspace && git add -A && git commit -m "<message>"`

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

After all tasks complete, commit:
```bash
cd mm-workspace && git add -A && git commit -m "feat(s3): all tasks solved - iteration {N}"
```

### Stage 3.5: Global Quality Review (invoke mm-review skill)

After Stage 3 completes, invoke the `mm-review` skill for global quality review.

**Input**: All workspace JSON files
**Output**: `mm-workspace/03.5_review.json`

#### Iteration Logic

```
iteration = 1
max_iterations = 3

while iteration <= max_iterations:
    # Run global review
    invoke mm-review skill
    read mm-workspace/03.5_review.json

    if review.overall_passed == true:
        cd mm-workspace && git tag review-pass-v{iteration}
        break  # Review passed, proceed to Stage 4

    else:
        # Review found issues
        Display review findings and rework_list to user

        if iteration == max_iterations:
            Ask: "已达到最大迭代次数({max_iterations})。是否接受当前结果并继续生成论文？"
            if user accepts:
                break
            else:
                Stop pipeline (user wants manual intervention)

        Ask: "审查发现以下问题（第 {iteration} 轮），是否进入第 {iteration+1} 轮迭代重修？"

        if user confirms:
            cd mm-workspace && git tag "review-iteration-{iteration}-needs-work"
            # Rework only the failed tasks
            for each task in rework_list:
                Re-run mm-solving for that specific task
            cd mm-workspace && git add -A && git commit -m "feat(s3): rework iteration {iteration+1}"
            iteration += 1
        else:
            break  # User accepts current results
```

**Key rules**:
- Maximum 3 iterations total (prevents infinite loops)
- Each iteration only reworks tasks identified in the rework_list (not all tasks)
- Git tag marks each iteration's status for traceability
- If user declines iteration or max reached, proceed with current results

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
