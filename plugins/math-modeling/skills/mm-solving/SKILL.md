---
name: mm-solving
description: >
  Stage 3 of the mathematical modeling pipeline. Solves each subtask by dispatching
  independent subagents that retrieve methods from HMML, generate formulas, write and
  execute Python code, and interpret results. Each task runs in a subagent to minimize
  main session context usage. Invoked by the math-modeling skill during Stage 3.
  Do not invoke directly.
version: 0.4.0
---

# Stage 3: Task Solving (Subagent-Dispatched)

## Purpose

Solve each subtask by dispatching independent subagents. Each subagent handles the full solve cycle (HMML retrieval → formulas → code → execution → verification → save). The main agent only handles scheduling, dispatch, and result summary.

**Why subagent dispatch**: Keeping the full solve cycle in the main session consumes excessive context. Subagents isolate each task's reasoning, keeping the main agent lean for orchestration.

## Input

- `mm-workspace/01_analysis.json` — problem analysis
- `mm-workspace/02_modeling.json` — modeling solution and task decomposition

## Main Agent Role: Dispatch & Collect

The main agent does NOT perform any task solving. It only:
1. Reads `02_modeling.json` to get DAG order and task definitions
2. Dispatches subagents for each task (respecting dependencies and concurrency limits)
3. Collects results from each subagent
4. Commits after each task and after all tasks complete

## Dispatch Process

### Step 1: Read DAG and Prepare

Read `mm-workspace/02_modeling.json` to extract:
- `dag_order` — execution sequence
- `tasks` — task definitions with dependencies

Build a dispatch plan:
1. Group tasks by dependency level (tasks with same dependencies can run in parallel)
2. Apply concurrency limit: max 2 subagents simultaneously

### Step 2: Dispatch Task Subagents

For each task (or batch of parallel tasks), use the Agent tool to dispatch a subagent with a comprehensive prompt containing everything it needs:

```
你是一名数学建模求解专家。请完成以下子任务的完整求解。

## 赛题背景
{Insert problem_text from 01_analysis.json}

## 建模方案概述
{Insert modeling_solution from 02_modeling.json}

## 当前任务定义
Task ID: {id}
描述: {description}
方法: {method}
期望输出: {expected_output}

## 前置任务结果
{For each dependency task_id:
  Read mm-workspace/03_task_{dep_id}.json
  Insert: task_id, key results, answer, output_files
}

## 求解步骤

请严格按照以下步骤执行：

### 1. HMML 方法检索
读取 reference 文件 references/hmml_index.md，根据任务类型加载相关领域文件（最多2个）。
选出 top-6 最相关方法，检查 hmml_index.md 中的"常见方法组合模式"。

### 2. 公式生成（Actor-Critic, 1轮）
读取 references/actor_critic.md。
- Actor: 生成数学公式（变量定义、方程、假设、边界条件）
- Critic（内联批评）: 检查公式正确性、创新性、可计算性、完整性
- Improvement: 改进公式

### 3. 建模过程详述
基于公式写出详细建模步骤。

### 4. 代码生成与执行
读取 references/code_templates.md 了解代码结构规范。
- 生成 Python 代码，保存到 mm-workspace/code/task_{id}.py
- 用 Bash 执行: cd {working_directory} && python mm-workspace/code/task_{id}.py
- 如果失败，调试最多 3 轮

### 5. 结果解读与回答
- 解读代码执行结果
- 生成完整回答

### 6. 结果验证
执行以下 4 项检查：
- 数值合理性：概率∈[0,1]、价格为正、无量级错误
- 跨任务一致性：与前置任务的结果和格式是否匹配
- 完整性：是否回答了该任务的所有子问题
- 领域含义：结果是否符合业务/物理常识

如果验证不通过，尝试修复一次。

### 7. 保存输出
将结果写入 mm-workspace/03_task_{id}.json，格式：
```json
{
  "task_id": {id},
  "analysis": "任务分析",
  "retrieved_methods": "top-6 方法",
  "formulas": "数学公式",
  "modeling_process": "建模过程",
  "code_path": "mm-workspace/code/task_{id}.py",
  "execution_success": true/false,
  "execution_result": "关键输出摘要",
  "result_interpretation": "结果解读",
  "answer": "完整回答",
  "verification": {
    "passed": true/false,
    "checks": [
      {"item": "numerical_sanity", "passed": true, "note": "..."},
      {"item": "cross_task_consistency", "passed": true, "note": "..."},
      {"item": "completeness", "passed": true, "note": "..."},
      {"item": "domain_meaning", "passed": true, "note": "..."}
    ]
  },
  "charts": ["mm-workspace/charts/task_{id}_fig1.png"],
  "output_files": ["mm-workspace/data/task_{id}_result.csv"],
  "stage": "task_complete"
}
```

然后执行: cd mm-workspace && git add -A && git commit -m "feat(s3): task {id} solved"

## 特殊情况：灵敏度分析

如果当前任务是灵敏度分析/鲁棒性检验，使用以下适配流程：
1. 读取所有前置任务输出，识别核心模型参数和假设
2. 设计灵敏度测试：参数扰动(±5%,±10%,±20%)、假设变化、数据噪声
3. 编写灵敏度分析代码（扰动循环 + 对比 + 灵敏度指标 + 可视化）
4. 解读结果：哪些参数/假设对模型最敏感

输出中增加 `"is_sensitivity_analysis": true`

## 注意事项
- 你必须独立完成所有步骤，不要请求用户输入
- 代码必须实际执行并保存结果
- 如果执行失败 3 次仍无法解决，标记 execution_success: false 并继续
- 生成的图表保存到 mm-workspace/charts/，数据保存到 mm-workspace/data/
```

### Step 3: Collect Results & Independent Verification

After each subagent completes:

**3a. Quick Check**
1. Read `mm-workspace/03_task_{id}.json` to verify it was saved correctly
2. Check `execution_success` is true and `verification.passed` is true

**3b. Independent Verification Subagent**

For each completed task, dispatch an **independent verification subagent** that does NOT inherit the solving context. This ensures the result is checked by a fresh perspective, not the same agent that produced it.

Use the Agent tool with this prompt:

```
你是一名独立的数学建模结果审核员。请对以下任务结果进行独立验证。

## 赛题原文摘要
{Insert problem_text from 01_analysis.json, truncated to 2 paragraphs}

## 任务定义
Task ID: {id}
描述: {description}
方法: {method}

## 任务求解结果
{Insert the full content of 03_task_{id}.json}

## 前置任务关键结果（用于一致性检查）
{For each dependency: task_id + answer + key numerical results}

## 验证要求

请逐项检查并给出 Pass / Fail：

1. **数值合理性**: 核心数值是否在合理范围？有无量级错误、符号错误、越界值？
2. **跨任务一致性**: 与前置任务的结论是否矛盾？输出格式是否匹配？
3. **完整性**: 任务描述中的每个子问题是否都有具体回答？要求的输出文件是否都生成了？
4. **领域含义**: 结果是否符合业务/物理常识？
5. **图表质量**: 如果生成了图表，是否清晰展示了关键结果？轴标签、图例是否完整？

## 输出格式

```json
{
  "task_id": {id},
  "independent_verification": {
    "passed": true/false,
    "checks": [
      {"item": "numerical_sanity", "passed": true/false, "note": "具体说明"},
      {"item": "cross_task_consistency", "passed": true/false, "note": "具体说明"},
      {"item": "completeness", "passed": true/false, "note": "具体说明"},
      {"item": "domain_meaning", "passed": true/false, "note": "具体说明"},
      {"item": "chart_quality", "passed": true/false, "note": "具体说明"}
    ],
    "issues_found": ["问题1", "问题2"],
    "severity": "none" | "minor" | "major"
  }
}
```
```

**3c. Process Verification Results**

Read the subagent's verification output:
- If `passed: true` or `severity: "none"/"minor"`: Accept the task result and proceed
- If `severity: "major"`: Note the issue but proceed (the global review in Stage 3.5 will catch it)
- Update `mm-workspace/03_task_{id}.json` with the `independent_verification` field

Display a brief summary to the user (2-3 sentences per task).

### Step 4: Final Commit

After all tasks complete:
```bash
cd mm-workspace && git add -A && git commit -m "feat(s3): all tasks solved - iteration {N}"
```

## Concurrency Control

**Hard constraint: max 2 concurrent subagents at any time.** This limit applies across ALL subagent types (task-solving, Critic, review).

### Batching Strategy

When N > 2 tasks can run in parallel:
1. Split into batches of 2: `[[task_a, task_b], [task_c, task_d], ...]`
2. Dispatch batch 1 (2 agents in parallel via Agent tool)
3. Wait for both to complete
4. Dispatch batch 2
5. Repeat until all parallel tasks are done
6. Proceed to dependent tasks

### Rules
- Each subagent works in its own isolated context — this is the key benefit for context management
- Ensure no file conflicts (each task writes to its own files)
- Wait for all parallel tasks in a batch to complete before dispatching dependent tasks
- Never dispatch more than 2 Agent tool calls simultaneously
- Subagents must be self-contained: include all necessary context in the dispatch prompt
