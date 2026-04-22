---
name: mm-review
description: >
  Stage 3.5 of the mathematical modeling pipeline. Performs global quality review
  of all task outputs using an independent subagent. Checks cross-task consistency,
  numerical credibility, requirement coverage, model coherence, evidence sufficiency,
  and chart/figure quality. Invoked by the math-modeling skill after Stage 3.
  Do not invoke directly.
version: 0.4.0
---

# Stage 3.5: Global Quality Review

## Purpose

After all tasks are solved (Stage 3), perform a comprehensive quality review of the entire modeling output. This review is conducted by an **independent subagent** that does not inherit the solving context, ensuring unbiased evaluation.

The goal is to answer: **Is the overall result good enough, or does it need rework?**

## Input

- `mm-workspace/01_analysis.json` — problem analysis
- `mm-workspace/02_modeling.json` — modeling solution and task decomposition
- `mm-workspace/03_task_{id}.json` — all task outputs (including verification results)

## Process

### Step 1: Collect All Outputs

Read all workspace files:
1. `mm-workspace/01_analysis.json` — extract the problem text and analysis
2. `mm-workspace/02_modeling.json` — extract task list and modeling approach
3. All `mm-workspace/03_task_*.json` files — extract results, answers, verification status

### Step 2: Dispatch Independent Review Subagent

Use the Agent tool to dispatch a general-purpose subagent with the following prompt:

```
你是一名资深的数学建模竞赛评审专家。请对以下完整的建模结果进行全局质量审查。

## 赛题原文
{Insert problem text from 01_analysis.json}

## 建模方案概述
{Insert modeling_solution from 02_modeling.json, truncated to key points}

## 任务列表及要求
{Insert tasks array from 02_modeling.json}

## 各任务求解结果
{For each task, insert:
  - task_id, description
  - execution_success
  - verification.passed and checks summary
  - independent_verification.passed and severity (if exists)
  - result_interpretation (key findings)
  - answer (main conclusions)
  - charts: list of generated chart files
}

## 生成的图表文件
{List all files in mm-workspace/charts/ directory}

## 审查维度（每项给出 Pass / Fail + 具体说明）

### 1. 结果一致性（Cross-Task Consistency）
各任务结果之间是否存在矛盾？
- 例如：Task 1 得出"A 方案最优"，Task 3 排序中 A 排第二
- 例如：Task 1 输出的数值范围与 Task 2 输入假设不匹配
- 例如：不同任务对同一变量的定义或取值不一致

### 2. 数值可信度（Numerical Credibility）
核心数值结果是否在合理范围？
- 是否存在量级错误（如人口 10^15）
- 是否存在符号错误（如成本为负）
- 是否存在百分比/概率超出 [0,1] 或 [0%,100%]
- 关键参数是否有数据支撑而非随意取值

### 3. 需求覆盖度（Requirement Coverage）
是否完整回答了赛题的所有子问题？
- 对照赛题原文，逐条检查是否都有对应回答
- 每个子问题是否有具体的数值结论（而非只有定性描述）
- 赛题要求的图表是否都已生成

### 4. 模型连贯性（Model Coherence）
各子模型之间的方法选择是否自洽？整体建模故事是否通顺？
- 方法选择是否有矛盾（如前面假设线性关系，后面用非线性模型）
- 各任务的方法是否形成一个完整的故事线
- 建模假设体系是否一致（不冲突）

### 5. 论据充分性（Evidence Sufficiency）
关键结论是否有充分的数据/图表/推导支撑？
- 核心结论是否只靠定性论述，缺少定量支撑
- 图表是否清晰展示关键结果
- 灵敏度分析是否充分

### 6. 图表质量（Chart & Figure Quality）
所有生成的图表是否达到论文发表水平？
- 是否存在空白图片、占位符、或生成失败的图表
- 轴标签、标题、图例是否完整且准确
- 配色是否清晰可区分（黑白打印也可辨识）
- 图表类型是否适合展示对应数据（如：分类比较用柱状图、趋势用折线图、分布用热力图）
- 每张图表是否有明确的结论性标题（不只是"结果"）
- 图表分辨率是否足够（非模糊截图）
- 赛题要求的图表是否都已生成

## 输出格式

```json
{
  "dimensions": [
    {"name": "cross_task_consistency", "passed": true/false, "details": "具体说明"},
    {"name": "numerical_credibility", "passed": true/false, "details": "具体说明"},
    {"name": "requirement_coverage", "passed": true/false, "details": "具体说明"},
    {"name": "model_coherence", "passed": true/false, "details": "具体说明"},
    {"name": "evidence_sufficiency", "passed": true/false, "details": "具体说明"},
    {"name": "chart_figure_quality", "passed": true/false, "details": "具体说明"}
  ],
  "overall_passed": true/false,
  "rework_list": [
    {
      "task_id": 2,
      "reason": "具体问题描述",
      "improvement_direction": "改进方向（不是完整方案）"
    }
  ],
  "summary": "一段话总结评审结论"
}
```

如果 overall_passed 为 false，rework_list 中必须列出需要重修的任务及具体原因。
如果 overall_passed 为 true，rework_list 为空数组。
```

### Step 3: Process Review Results

Receive the subagent's review output. Parse the JSON response.

If **overall_passed = true**:
- All 5 dimensions passed
- Save review results and proceed

If **overall_passed = false**:
- At least one dimension failed
- Extract the `rework_list`
- Present findings to user

### Step 4: Save Review Output

Write to `mm-workspace/03.5_review.json`:

```json
{
  "iteration": 1,
  "overall_passed": true,
  "dimensions": [
    {"name": "cross_task_consistency", "passed": true, "details": "..."},
    {"name": "numerical_credibility", "passed": true, "details": "..."},
    {"name": "requirement_coverage", "passed": true, "details": "..."},
    {"name": "model_coherence", "passed": true, "details": "..."},
    {"name": "evidence_sufficiency", "passed": true, "details": "..."},
    {"name": "chart_figure_quality", "passed": true, "details": "..."}
  ],
  "rework_list": [],
  "summary": "review summary text",
  "stage": "review_complete"
}
```

Then commit: `cd mm-workspace && git add -A && git commit -m "feat(s3.5): global review - iteration {N}"`
