---
name: mm-solving
description: >
  Stage 3 of the mathematical modeling pipeline. Solves each subtask by dispatching
  independent subagents that retrieve methods from HMML, generate formulas, write and
  execute Python code, and interpret results. Each task runs in a subagent to minimize
  main session context usage. Invoked by the math-modeling skill during Stage 3.
  Do not invoke directly.
version: 0.4.4
---

# Stage 3: Task Solving (Subagent-Dispatched)

## Purpose

Solve each subtask by dispatching independent subagents. Each subagent handles the full solve cycle (HMML retrieval → formulas → code → execution → verification → save). The main agent only handles scheduling, dispatch, and result summary.

**Why subagent dispatch**: Keeping the full solve cycle in the main session consumes excessive context. Subagents isolate each task's reasoning, keeping the main agent lean for orchestration.

## Input

- `mm-workspace/01_analysis.json` — problem analysis
- `mm-workspace/02_modeling.json` — modeling solution and task decomposition
- `mm-workspace/pipeline_state.json` — pipeline state with known_issues (v0.4.4)

## Main Agent Role: Dispatch & Collect

The main agent does NOT perform any task solving. It only:
1. Reads `02_modeling.json` to get DAG order and task definitions
2. Reads `pipeline_state.json` for known_issues to pass to subagents
3. Dispatches subagents for each task (respecting dependencies and concurrency limits)
4. Collects results from each subagent
5. Validates schema compliance (v0.4.4 强化)
6. Commits after each task and after all tasks complete

## Dispatch Process

### Step 1: Read DAG and Prepare

Read `mm-workspace/02_modeling.json` to extract:
- `dag_order` — execution sequence
- `tasks` — task definitions with dependencies

Read `mm-workspace/pipeline_state.json` to extract:
- `stage_3_tasks` — per-task completion status
- `known_issues` — accumulated warnings from previous tasks

Build a dispatch plan:
1. Group tasks by dependency level (tasks with same dependencies can run in parallel)
2. Apply concurrency limit: max 2 subagents simultaneously
3. **Fallback (v0.4.4)**: If parallel dispatch is not technically feasible, sequential execution is acceptable. Do not block the pipeline on parallelism.

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

## 已知问题和警告 (v0.4.4 新增)
{Read pipeline_state.json known_issues array. For each issue relevant to current task:
  - source_task: N, type: "...", detail: "..."
Include ALL known issues from dependent tasks. If no known issues, write "无"}

## 求解步骤

请严格按照以下步骤执行：

### 1. HMML 方法检索 (必须执行，不可跳过)
读取 reference 文件 references/hmml_index.md，根据任务类型加载相关领域文件（最多2个）。
选出 top-6 最相关方法，检查 hmml_index.md 中的"常见方法组合模式"。
**此步骤不可跳过。** 将选出的方法列表写入输出 JSON 的 retrieved_methods 字段。

### 2. 公式生成（Actor-Critic, 自适应 1-3 轮, 通过线 80 分）
读取 references/actor_critic.md。
- Actor: 生成数学公式（变量定义、方程、假设、边界条件）
- Critic（内联批评）: 按以下维度百分制评分：

| 维度 | 权重 | 60分线 |
|------|------|--------|
| 代码执行 | 25 | 代码成功运行并输出结果 |
| 结果合理性 | 25 | 数值在合理范围 |
| 完整性 | 20 | 所有子问题已回答 |
| 方法质量 | 15 | 方法合适且运用正确 |
| 图表产出 | 15 | 需要可视化的部分已生成 |

通过线：80 分。代码执行 < 10 分则总分封顶 59。
- Improvement: 根据 improvement_directions 改进
- 自适应迭代：总分 ≥ 80 通过；< 80 且轮次 < 3 则迭代；第 3 轮 < 60 则标记失败

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
执行以下检查：
- 数值合理性：概率∈[0,1]、价格为正、无量级错误
- 跨任务一致性：与前置任务的结果和格式是否匹配
- 完整性：是否回答了该任务的所有子问题
- 领域含义：结果是否符合业务/物理常识
- 循环论证：验证所用信息是否与估计信息本质重叠
- 拟合质量：回归任务 R² < 0.3 时需在结果中标注警告
- 退化检测：优化参数是否退化为平凡解

如果验证不通过，尝试修复一次。

### 7. 保存输出 (v0.4.4 schema 强制)
将结果写入 mm-workspace/03_task_{id}.json，**必须包含以下所有字段**：

```json
{
  "task_id": {id},
  "analysis": "任务分析",
  "retrieved_methods": "HMML top-6 方法描述",
  "formulas": "数学公式（LaTeX）",
  "modeling_process": "建模过程详述",
  "code_path": "mm-workspace/code/task_{id}.py",
  "execution_success": true/false,
  "execution_result": "关键输出摘要",
  "result_interpretation": "结果解读",
  "answer": "完整回答（至少 50 字符）",
  "verification": {
    "passed": true/false,
    "checks": [
      {"item": "numerical_sanity", "passed": true, "note": "..."},
      {"item": "cross_task_consistency", "passed": true, "note": "..."},
      {"item": "completeness", "passed": true, "note": "..."},
      {"item": "domain_meaning", "passed": true, "note": "..."},
      {"item": "circular_reasoning", "passed": true, "note": "..."},
      {"item": "model_fit_quality", "passed": true, "note": "..."},
      {"item": "optimization_degeneracy", "passed": true, "note": "..."}
    ]
  },
  "charts": ["mm-workspace/charts/task_{id}_fig1.png"],
  "output_files": ["mm-workspace/data/task_{id}_result.csv"],
  "stage": "task_complete"
}
```

**Schema 合规是强制性的 (v0.4.4)**:
- 以上 JSON 中每个字段都必须存在且类型正确
- `verification.checks` 数组长度 >= 4
- `answer` 字符串长度 > 50
- `code_path` 指向的文件必须存在
- 缺少任何字段将导致主代理的 schema 验证失败（见 Step 3a.5）

**重要：子代理不执行 git commit。** git 操作由主代理在验证完成后执行。子代理只负责保存 JSON 和代码文件。

## 特殊情况：灵敏度分析

如果当前任务是灵敏度分析/鲁棒性检验，必须覆盖两个层次：

### 层次 1: 核心估计模型鲁棒性
对主要估计模型（如粉丝投票估计、参数拟合等）的参数扰动：
- 关键参数 ±10% 扰动，观察输出变化幅度
- 报告弹性系数：参数变化 1% → 结果变化 X%
- 识别最敏感的参数和假设
- 检验估计结果本身的稳定性

### 层次 2: 最终系统/结论鲁棒性
对最终推荐方案（如公平投票系统）的参数扰动：
- 系统参数的灵敏度分析
- 假设变化测试（方法变更边界、噪声注入等）
- 交叉验证（留一法等）

**不允许只做层次 2 不做层次 1。两个层次都是必需的。**

### 测试项优先级 (v0.4.4 新增)

| 优先级 | 测试项 | 说明 |
|--------|--------|------|
| REQUIRED | 关键参数 ±10% 扰动 | 所有模型核心参数 |
| REQUIRED | 弹性系数报告 | 参数变化 → 结果变化 |
| REQUIRED | 最敏感参数识别 | tornado plot |
| RECOMMENDED | 假设变化测试 | 方法变更边界 |
| RECOMMENDED | 系统参数灵敏度 | 最终系统参数 |
| OPTIONAL | 留一法交叉验证 | 计算量大，如时间允许则执行 |

如果 context 或时间有限，优先完成 REQUIRED 项，RECOMMENDED 项尽量完成，OPTIONAL 项可跳过但需在结果中说明。

### 输出要求
- 灵敏度龙卷风图（tornado plot）
- 交叉验证准确率按赛季/折的图表（如执行了交叉验证）
- 明确结论：哪些参数/假设对最终结论影响最大

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

**3a.5. Output Schema Validation (v0.4.4 强化)**

Read `mm-workspace/03_task_{id}.json` and validate required fields:

| Field | Type | Requirement | On Missing |
|-------|------|-------------|------------|
| task_id | int | Must equal current task ID | ERROR — must fix |
| execution_success | bool | Must exist | ERROR — must fix |
| stage | string | Must be "task_complete" | Backfill if possible |
| verification.passed | bool | Must exist | ERROR — must fix |
| verification.checks | array | Length >= 4 | ERROR — must fix |
| answer | string | Length > 50 characters | Backfill from result_interpretation |
| charts | array | Must exist (can be empty) | Default to [] |
| result_interpretation | string | Must exist | Backfill from answer |
| code_path | string | Must point to existing file | ERROR — must fix |
| retrieved_methods | string | Must exist (HMML retrieval) | Backfill "N/A" |
| formulas | string | Must exist | Backfill from modeling_process |
| modeling_process | string | Must exist | Backfill from analysis |

**Validation failure handling (v0.4.4)**:
1. **ERROR 级别缺失**: 核心字段。尝试从子代理输出中提取并回填（backfill）。如果回填失败，在 JSON 中标记 `"_schema_incomplete": true`，并写入 `pipeline_state.json` 的 `known_issues`
2. **Backfill 级别缺失**: 从子代理的其他输出字段推断并填充
3. **所有 backfill 尝试最多 1 次**，不要反复修复

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

## 已知问题 (v0.4.4)
{Insert any known_issues from pipeline_state.json that are relevant to this task or its dependencies. If none, write "无已知问题"}

## 验证要求

请逐项检查并给出 Pass / Fail：

1. **数值合理性**: 核心数值是否在合理范围？有无量级错误、符号错误、越界值？
2. **跨任务一致性**: 与前置任务的结论是否矛盾？输出格式是否匹配？
3. **完整性**: 任务描述中的每个子问题是否都有具体回答？要求的输出文件是否都生成了？
4. **领域含义**: 结果是否符合业务/物理常识？
5. **图表质量**: 如果生成了图表，是否清晰展示了关键结果？轴标签、图例是否完整？
6. **循环论证检测**: 验证方法是否与估计方法本质相同？验证所用的信息是否已隐含在估计过程中？典型案例：用约束满足估计排名 → 再用排名准确率验证 → 天然 100%，属同义反复。如果检测到循环论证，severity 直接标记为 "major"。
7. **模型拟合质量评估**: 回归任务 R² < 0.3 为弱拟合（警告），R² < 0.1 为严重问题；分类任务准确率低于多数类基线为严重问题。弱拟合不等于失败，但需确认后续结论已做降级表述。
8. **优化结果退化检测**: 最优参数是否退化到退化解？最优点是否在搜索空间的极端位置？参数是否触及 clip 边界？典型案例：权重函数 λ→1.0 退化为纯评委系统。如果检测到退化，建议调整搜索空间或增加约束。
9. **指标定义一致性**: 跨任务使用的同名指标是否定义相同？典型案例："ranking_accuracy" 在 Task 2 中为约束满足率，在 Task 6 中为回归预测率。同名指标数值量级差异 > 10x 则标记为可疑。
10. **方法选择-实际使用一致性**: BIC/AIC 选出的最佳方法是否确实是最终报告和推荐中使用的方法？如果 BIC 选择了方法 A 但最终推荐使用方法 B，需要检查是否有合理理由。无理由的切换应标记为 "major"。

## 输出格式

严格按以下 JSON 格式输出，不要有多余文字：
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
      {"item": "chart_quality", "passed": true/false, "note": "具体说明"},
      {"item": "circular_reasoning", "passed": true/false, "note": "具体说明"},
      {"item": "model_fit_quality", "passed": true/false, "note": "具体说明"},
      {"item": "optimization_degeneracy", "passed": true/false, "note": "具体说明"},
      {"item": "metric_definition_consistency", "passed": true/false, "note": "具体说明"},
      {"item": "method_selection_consistency", "passed": true/false, "note": "具体说明"}
    ],
    "issues_found": ["问题1", "问题2"],
    "severity": "none" | "minor" | "major"
  }
}
```
```

**3c. Process Verification Results (v0.4.4 强化)**

Read the subagent's verification output:
1. If `passed: true` or `severity: "none"/"minor"`: Accept the task result
2. If `severity: "major"`: Note the issue, add to `pipeline_state.json` `known_issues` array with format `{"source_task": id, "type": "verification_major", "detail": "问题摘要"}`
3. **MUST update `mm-workspace/03_task_{id}.json`**: Read the file, add the `independent_verification` object from the verification subagent, and write it back. The verification result MUST be embedded in the task JSON's `independent_verification` field, not saved as a separate file.

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

### Parallel Dispatch Fallback (v0.4.4)

If the Agent tool does not support parallel dispatch in your environment, sequential execution is acceptable. The parallelism hint in `02_modeling.json` `parallel_groups` is a recommendation, not a requirement. **Do not block the pipeline if parallel dispatch fails.**

## Fix Verification Loop (v0.4.4 新增)

When a task is fixed (either through schema validation backfill or rework):

1. Re-run schema validation (Step 3a.5) on the fixed `03_task_{id}.json`
2. If still fails: mark `_schema_incomplete: true`, add to `known_issues`, proceed
3. **Max 1 fix attempt per issue type** — do not enter infinite fix-validate loops
4. If the fix required code re-execution, re-run independent verification (Step 3b) for the fixed task
