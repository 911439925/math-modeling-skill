---
name: math-modeling
description: >
  Universal mathematical modeling agent for all competitions. Activates when
  the user mentions "math modeling", "mathematical modeling", "美赛", "国赛", "建模",
  "MCM", "ICM", "MathorCup", or asks to solve a modeling competition problem.
  Also use when the user wants to analyze a problem, build a mathematical model,
  decompose it into subtasks, and solve each subtask with code execution.
  Covers the complete workflow from problem understanding to LaTeX paper generation.
version: 0.4.4
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

## Pipeline State Machine (v0.4.4 新增)

**核心机制**: 流水线的每个阶段受 `pipeline_state.json` 状态文件控制。该文件是阶段转换的唯一权威——任何阶段开始前必须校验前置状态，完成后必须更新状态。

### 状态文件格式

写入 `mm-workspace/pipeline_state.json`：

```json
{
  "version": "0.4.4",
  "current_stage": "initialization",
  "stages": {
    "initialization": "complete",
    "stage_1_analysis": "pending",
    "stage_2_modeling": "pending",
    "stage_3_solving": "pending",
    "stage_3_tasks": {},
    "stage_3_5_review": "pending",
    "stage_4_paper": "pending"
  },
  "stage_3_5_passed": false,
  "known_issues": [],
  "last_updated": ""
}
```

### 阶段状态值

每个阶段：`pending` → `running` → `complete`

### 前置条件表

| 目标阶段 | 前置阶段（须 complete） | 必需文件 |
|-----------|------------------------|---------|
| `stage_1_analysis` | `initialization` | (无) |
| `stage_2_modeling` | `stage_1_analysis` | `01_analysis.json` |
| `stage_3_solving` | `stage_2_modeling` | `01_analysis.json`, `02_modeling.json` |
| `stage_3_5_review` | `stage_3_solving` | 所有 `03_task_*.json` |
| `stage_4_paper` | `stage_3_5_review` | `03.5_review.json` |

### 阶段转换守卫

**每个阶段开始前 MUST 执行：**

1. 读取 `pipeline_state.json`
2. 检查前置阶段状态为 `"complete"`
3. 检查必需文件物理存在
4. 如果目标是 `stage_4_paper`：额外检查 `stage_3_5_passed == true`
5. 全部通过 → 更新阶段为 `"running"`，保存 `pipeline_state.json`
6. 任一失败 → STOP 并告知用户缺少什么

### 阶段完成后更新

1. 将该阶段状态改为 `"complete"`
2. 更新 `current_stage` 为下一阶段名称
3. 如果是 Stage 3.5 且通过，设置 `stage_3_5_passed: true`
4. 用 Write 工具保存 `pipeline_state.json`

## Workflow

## Global Constraints

- **Max concurrent subagents**: 2. This includes Critic subagents (improvement A) and task-solving subagents. Never dispatch more than 2 Agent tool calls simultaneously. Batch parallel tasks into groups of 2 maximum.
- **Stage 3.5 (Global Review) is MANDATORY and MUST NOT be skipped.** After Stage 3 completes, you MUST invoke mm-review before proceeding to Stage 4. There are NO exceptions. Even if you think the results are good, the independent review must run. Skipping Stage 3.5 to save time is a pipeline violation.
- **Task solving via subagents**: All Stage 3 tasks must be dispatched to subagents to minimize main session context consumption. The main agent must not perform detailed solving work inline.
- **Independent verification per task**: After each task subagent completes, dispatch an independent verification subagent before proceeding to the next task. **This is a mandatory gate, not an optional step.** You MUST NOT dispatch the next task until the current task's verification is complete. Violating this is the same severity as skipping Stage 3.5.

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

3. Initialize pipeline state: Write `mm-workspace/pipeline_state.json` with `initialization: "complete"` and all other stages `"pending"`. For `stage_3_tasks`, populate keys from `02_modeling.json` tasks after Stage 2 completes.

4. Read and extract the problem:
   - If the user provides a file path (PDF, image, text), read it using the Read tool
   - If the user provides text directly, use it as the problem
   - Identify if there are attached dataset files
   - Save the raw problem to `mm-workspace/raw_problem.txt`

5. Detect competition type if user mentions it (affects paper template and language)

### Git Commit Protocol

After each stage or significant milestone, commit workspace state:

| 时机 | commit message | 必须执行 |
|------|---------------|---------|
| Stage 1 完成后 | `feat(s1): problem analysis complete` | YES |
| Stage 2 完成后 | `feat(s2): modeling and decomposition complete` | YES |
| Stage 3 每个任务完成后 | `feat(s3): task {id} solved` | YES |
| Stage 3 全部完成（每轮迭代） | `feat(s3): all tasks solved - iteration {N}` | YES |
| 全局审查通过后 | `git tag review-pass-v{N}` | YES |
| 全局审查未通过（迭代中） | `git tag review-iteration-{N}-score-{score}` | YES |
| Stage 4 完成后 | `feat(s4): paper generated` | YES |
| 最终定稿 | `git tag final-v{N}` | YES |

Commit command: `cd mm-workspace && git add -A && git commit -m "<message>"`

**Git 执行规则 (v0.4.4 强化)**:
- 每个 commit/tag 标记为 YES，不可跳过
- 在 Per-Task Execution Gate 的 Step 8 中执行 git commit，写死在流程中
- 如果 commit 失败，先修复问题再继续——不要在没有 commit 的情况下进入下一步
- Tag 必须在对应事件发生后立即创建，不能延后批量创建

### Stage 1: Problem Analysis (invoke mm-analysis skill)

**前置检查**: 读取 `pipeline_state.json`，验证 `initialization` 为 `"complete"`。否则 STOP。

After initialization, invoke the `mm-analysis` skill to perform deep problem analysis.

**Input**: Problem text + dataset files (if any)
**Output**: `mm-workspace/01_analysis.json`

After Stage 1 completes:
- Update `pipeline_state.json`: `stage_1_analysis: "complete"`
- Present the analysis summary and Critic score to the user
- If score >= 75: Ask "问题分析完成（得分 {score}/100），是否需要修改？确认后进入建模阶段。"
- If 60 <= score < 75 after 3 rounds: Warn and ask to proceed or revise
- If score < 60 after 3 rounds: Pause, present critical issues, let user decide
- Wait for user confirmation before proceeding

### Stage 2: Modeling & Decomposition (invoke mm-modeling skill)

**前置检查**: 读取 `pipeline_state.json`，验证 `stage_1_analysis` 为 `"complete"`，且 `01_analysis.json` 存在。否则 STOP。

After user confirms Stage 1, invoke the `mm-modeling` skill.

**Input**: `mm-workspace/01_analysis.json`
**Output**: `mm-workspace/02_modeling.json`

After Stage 2 completes:
- Update `pipeline_state.json`: `stage_2_modeling: "complete"`，并从 `02_modeling.json` 的 tasks 数组填充 `stage_3_tasks` 的 key
- Present the modeling solution, task decomposition, and Critic score to the user
- If score >= 75: Ask "建模方案完成（得分 {score}/100），是否需要修改？确认后开始逐任务求解。"
- If 60 <= score < 75 after 3 rounds: Warn and ask to proceed or revise
- If score < 60 after 3 rounds: Pause, present critical issues, let user decide
- Wait for user confirmation before proceeding

### Stage 3: Task Solving (invoke mm-solving skill)

**前置检查**: 读取 `pipeline_state.json`，验证 `stage_2_modeling` 为 `"complete"`，且 `01_analysis.json` + `02_modeling.json` 均存在。否则 STOP。

After user confirms Stage 2, invoke the `mm-solving` skill for each task in DAG order.

**Input**: `mm-workspace/01_analysis.json` + `mm-workspace/02_modeling.json`
**Output**: `mm-workspace/03_task_{id}.json` for each task

Update `pipeline_state.json`: `stage_3_solving: "running"`

#### Per-Task Execution Gate (MANDATORY)

For each task, you MUST follow these steps **in strict order**. Do NOT skip any step or reorder them:

```
for each task in dag_order:
    1. DISPATCH task subagent (invoke mm-solving)
    2. WAIT for subagent to complete
    3. COLLECT: Read 03_task_{id}.json, verify execution_success
    4. VALIDATE: Run schema validation (mm-solving Step 3a.5)
       - If validation fails: attempt backfill (max 1 attempt)
       - If backfill fails: mark _schema_incomplete: true, LOG ERROR, add to pipeline_state.json known_issues
    5. VERIFY: Dispatch independent verification subagent (mm-solving Step 3b)
    6. WAIT for verification subagent to complete
    7. PROCESS: Review verification results, update JSON (mm-solving Step 3c)
       - If severity == "major": add to pipeline_state.json known_issues array
    8. COMMIT: cd mm-workspace && git add -A && git commit -m "feat(s3): task {id} solved"
    9. CHECK: Run cross-task consistency quick check (see below)
    10. UPDATE STATE: Update pipeline_state.json stage_3_tasks[id] = "complete"
    → ONLY THEN proceed to next task
```

**DO NOT** dispatch the next task until steps 1-10 are complete for the current task.
**DO NOT** parallelize task solving with verification of a previous task.
**DO NOT** skip the verification subagent (Step 5) to save time.
**DO NOT** skip the git commit (Step 8) — it is not optional.

#### 跨任务一致性快速检查（每个 Task 完成后主代理执行）

每个 Task 子代理返回后，运行跨任务一致性检查脚本：

```bash
python scripts/cross_task_consistency.py mm-workspace --current-task {id}
```

该脚本自动执行以下检查：

1. **JSON 格式完整性**: 校验 `03_task_{id}.json` 必填字段
2. **指标名称冲突**: 提取当前 Task 所有量化指标名称，与已完成 Task 比较
   - 同名但数值量级差异 > 10x → 标记警告
3. **数值传递链**: 根据 `02_modeling.json` 的 DAG 依赖关系
   - 验证当前 Task 使用的输入值 ≈ 前置 Task 报告的输出值
   - 偏差 > 5% → 标记警告

脚本输出包含 `known_issues` 格式的 JSON 数组，可直接追加到 `pipeline_state.json` 的 `known_issues` 字段。

**检查结果处理 (v0.4.4 强化)**:
- 警告写入 `pipeline_state.json` 的 `known_issues` 数组
- 格式: `{"source_task": N, "type": "cross_task_warning", "detail": "具体描述"}`
- 这些警告会在后续 task 的 dispatch prompt 中作为"已知问题"传递（见 mm-solving Step 2）
- 问题留给 Stage 3.5 全局审查深入处理

After all tasks complete:
```bash
cd mm-workspace && git add -A && git commit -m "feat(s3): all tasks solved - iteration {N}"
```
Update `pipeline_state.json`: `stage_3_solving: "complete"`

### Stage 3.5: Global Quality Review (invoke mm-review skill)

**前置检查**: 读取 `pipeline_state.json`，验证 `stage_3_solving` 为 `"complete"`。否则 STOP 并返回完成未完成的任务。

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
        update pipeline_state.json: stage_3_5_review = "complete", stage_3_5_passed = true
        break  # Review passed, proceed to Stage 4

    elif score >= 60:
        # Improvable but not critical
        Display review scores and rework_list to user

        if iteration == max_iterations:
            Ask: "已达到最大迭代次数({max_iterations})，当前得分 {score}。是否接受当前结果并继续生成论文？"
            if user accepts:
                update pipeline_state.json: stage_3_5_review = "complete", stage_3_5_passed = true
                break
            else:
                Stop pipeline

        Ask: "审查得分 {score}/{pass_threshold}（第 {iteration} 轮），是否进入第 {iteration+1} 轮迭代重修？"

        if user confirms:
            cd mm-workspace && git tag "review-iteration-{iteration}-score-{score}"
            for each task in rework_list:
                Re-run mm-solving for that specific task
                Update pipeline_state.json stage_3_tasks[id] = "complete"
            cd mm-workspace && git add -A && git commit -m "feat(s3): rework iteration {iteration+1}"
            iteration += 1
        else:
            update pipeline_state.json: stage_3_5_review = "complete", stage_3_5_passed = true
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

**前置检查 (v0.4.4 硬性，不可绕过)**:
1. 读取 `pipeline_state.json`
2. 验证 `stage_3_5_review` 状态为 `"complete"`
3. 验证 `stage_3_5_passed` 为 `true`
4. 验证 `mm-workspace/03.5_review.json` 文件物理存在

**如果以上任一条件不满足 → STOP。你跳过了 Stage 3.5。回到 Stage 3.5 执行全局审查。没有任何理由可以绕过此检查。**

After all checks pass, invoke the `mm-writing` skill for LaTeX paper generation.

**Input**: All workspace JSON files + code + charts
**Output**: `mm-workspace/05_paper/main.tex` → compiled `mm-workspace/05_paper/main.pdf`

After Stage 4 completes:
- Update `pipeline_state.json`: `stage_4_paper: "complete"`
- `cd mm-workspace && git tag final-v{N}`

See `mm-writing` skill for details.

### Final Summary

After paper generation:
- Summarize all task results and paper output
- List all generated files (code, data, charts, paper)
- Provide the PDF file path

## Error Recovery

- If any stage fails, save progress to workspace JSON files and update `pipeline_state.json`
- The user can resume from the last completed stage by checking `pipeline_state.json`
- If a task's code fails after 3 debug rounds, mark it as failed and continue with other tasks
- **Fix verification loop (v0.4.4 新增)**: When a task is fixed after failure, you MUST re-run schema validation (mm-solving Step 3a.5) on the fixed output. If the fix still doesn't pass validation, do not re-fix blindly — add `_schema_incomplete: true` and log the issue
- Never delete workspace files without user confirmation

## Key References

Load these reference files as needed:
- `references/hmml_index.md` - HMML method index (load first during Stage 3)
- `references/hmml_*.md` - HMML domain files (load relevant domains only)
- `references/actor_critic.md` - Actor-Critic mechanism guide
- `references/dag_scheduler.md` - DAG scheduling strategy
- `references/code_templates.md` - Code template specification
- `references/abstract_guide.md` - Abstract generation guide
