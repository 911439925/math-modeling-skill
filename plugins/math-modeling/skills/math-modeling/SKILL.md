---
name: math-modeling
description: >
  Universal mathematical modeling agent for all competitions. Activates when
  the user mentions "math modeling", "mathematical modeling", "美赛", "国赛", "建模",
  "MCM", "ICM", "MathorCup", or asks to solve a modeling competition problem.
  Also use when the user wants to analyze a problem, build a mathematical model,
  decompose it into subtasks, and solve each subtask with code execution.
  Covers the complete workflow from problem understanding to LaTeX paper generation.
version: 0.4.2
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
- **Stage 3.5 (Global Review) is MANDATORY and MUST NOT be skipped.** After Stage 3 completes, you MUST invoke mm-review before proceeding to Stage 4. There are NO exceptions. Even if you think the results are good, the independent review must run. Skipping Stage 3.5 to save time is a pipeline violation.
- **Task solving via subagents**: All Stage 3 tasks must be dispatched to subagents to minimize main session context consumption. The main agent must not perform detailed solving work inline.
- **Independent verification per task**: After each task subagent completes, dispatch an independent verification subagent before proceeding to the next task.

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
- Present the analysis summary and Critic score to the user
- If score >= 75: Ask "问题分析完成（得分 {score}/100），是否需要修改？确认后进入建模阶段。"
- If 60 <= score < 75 after 3 rounds: Warn and ask to proceed or revise
- If score < 60 after 3 rounds: Pause, present critical issues, let user decide
- Wait for user confirmation before proceeding

### Stage 2: Modeling & Decomposition (invoke mm-modeling skill)

After user confirms Stage 1, invoke the `mm-modeling` skill.

**Input**: `mm-workspace/01_analysis.json`
**Output**: `mm-workspace/02_modeling.json`

After Stage 2 completes:
- Present the modeling solution, task decomposition, and Critic score to the user
- If score >= 75: Ask "建模方案完成（得分 {score}/100），是否需要修改？确认后开始逐任务求解。"
- If 60 <= score < 75 after 3 rounds: Warn and ask to proceed or revise
- If score < 60 after 3 rounds: Pause, present critical issues, let user decide
- Wait for user confirmation before proceeding

### Stage 3: Task Solving (invoke mm-solving skill)

After user confirms Stage 2, invoke the `mm-solving` skill for each task in DAG order.

**Input**: `mm-workspace/01_analysis.json` + `mm-workspace/02_modeling.json`
**Output**: `mm-workspace/03_task_{id}.json` for each task

Task solving runs **automatically** through all tasks:
- Solve each task following the mm-solving skill instructions
- Display task results as they complete
- Only pause if a task fails or user explicitly interrupts

#### 跨任务一致性快速检查（每个 Task 完成后主代理执行）

每个 Task 子代理返回后，主代理在 collect 阶段执行以下快速检查：

1. **JSON 格式完整性**: 校验 `03_task_{id}.json` 必填字段（见 mm-solving Step 3a.5）
2. **指标名称冲突**: 提取当前 Task 所有量化指标名称，与已完成 Task 比较
   - 同名但数值量级差异 > 10x → 标记警告
   - 同名但含义不同 → 标记警告
3. **数值传递链**: 如果当前 Task 依赖前置 Task 的数值输出
   - 验证当前 Task 使用的输入值 ≈ 前置 Task 报告的输出值
   - 偏差 > 5% → 标记警告

检查结果不阻塞流程，但显示为警告信息。问题留给 Stage 3.5 全局审查深入处理。

After all tasks complete, commit:
```bash
cd mm-workspace && git add -A && git commit -m "feat(s3): all tasks solved - iteration {N}"
```

### Stage 3.5: Global Quality Review (invoke mm-review skill)

**This stage is MANDATORY. Do NOT skip it. Do NOT go directly to Stage 4.**

After Stage 3 completes, you MUST invoke the `mm-review` skill for global quality review. This is non-negotiable — the independent review catches issues that the solving process cannot self-detect.

**Input**: All workspace JSON files
**Output**: `mm-workspace/03.5_review.json`

#### Iteration Logic

```
iteration = 1
max_iterations = 3
pass_threshold = 80  # Stage 3.5 通过线

while iteration <= max_iterations:
    # Run global review
    invoke mm-review skill
    read mm-workspace/03.5_review.json
    score = review.total

    if score >= pass_threshold:
        cd mm-workspace && git tag review-pass-v{iteration}
        break  # Review passed, proceed to Stage 4

    elif score >= 60:
        # Improvable but not critical
        Display review scores and rework_list to user

        if iteration == max_iterations:
            Ask: "已达到最大迭代次数({max_iterations})，当前得分 {score}。是否接受当前结果并继续生成论文？"
            if user accepts:
                break
            else:
                Stop pipeline

        Ask: "审查得分 {score}/{pass_threshold}（第 {iteration} 轮），是否进入第 {iteration+1} 轮迭代重修？"

        if user confirms:
            cd mm-workspace && git tag "review-iteration-{iteration}-score-{score}"
            for each task in rework_list:
                Re-run mm-solving for that specific task
            cd mm-workspace && git add -A && git commit -m "feat(s3): rework iteration {iteration+1}"
            iteration += 1
        else:
            break

    else:
        # score < 60: fundamental issues
        Display critical failure with specific dimension scores

        if iteration == max_iterations:
            PAUSE pipeline
            Ask: "第 {max_iterations} 轮审查得分 {score}，低于及格线 60 分。请选择：1) 提供指导后重试  2) 接受当前结果  3) 终止流水线"
            user decides → proceed accordingly
        else:
            Ask: "审查得分 {score}（第 {iteration} 轮），存在基础性问题。是否进入第 {iteration+1} 轮迭代？"
            if user confirms:
                rework and iterate
            else:
                break
```

**Key rules**:
- Maximum 3 iterations total (prevents infinite loops)
- Score >= 80: pass automatically
- 60 <= score < 80: improvable, iterate with user consent
- Score < 60: fundamental issues, pause for user decision
- Each iteration only reworks tasks identified in the rework_list
- Git tag marks each iteration's score for traceability

### Stage 4: Paper Generation (invoke mm-writing skill)

**Pre-condition: Stage 3.5 must have completed.** Before invoking mm-writing, verify that `mm-workspace/03.5_review.json` exists. If it does not exist, you have skipped Stage 3.5 — go back and run it now.

After all tasks complete and Stage 3.5 has passed, invoke the `mm-writing` skill for LaTeX paper generation.

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
