---
name: mm-review
description: >
  Stage 3.5 of the mathematical modeling pipeline. Performs global quality review
  of all task outputs using an independent subagent with percent-based scoring.
  Checks cross-task consistency, numerical credibility, requirement coverage,
  model coherence, evidence sufficiency, and chart/figure quality.
  Invoked by the math-modeling skill after Stage 3. Do not invoke directly.
version: 0.4.1
---

# Stage 3.5: Global Quality Review

## Purpose

After all tasks are solved (Stage 3), perform a comprehensive quality review of the entire modeling output. This review is conducted by an **independent subagent** that does not inherit the solving context, ensuring unbiased evaluation.

The goal is to answer: **Is the overall result good enough, or does it need rework?**

## Input

- `mm-workspace/01_analysis.json` — problem analysis
- `mm-workspace/02_modeling.json` — modeling solution and task decomposition
- `mm-workspace/03_task_{id}.json` — all task outputs (including verification results)

## Scoring Criteria

通过线：**80 分**。硬性否决：任意维度 < 10 分 → 总分封顶 59。

| 维度 | 权重 | 60分线 | 满分要求 |
|------|------|--------|---------|
| 结果一致性 | 20 | 各任务结果无直接矛盾 | 跨任务数值和结论完全自洽 |
| 数值可信度 | 20 | 核心数值无重大错误 | 所有数值有据可查 |
| 需求覆盖度 | 20 | 所有子问题有回答 | 每个子问题有定量结论+图表 |
| 模型连贯性 | 15 | 方法选择无明显矛盾 | 方法故事线完整通顺 |
| 论据充分性 | 15 | 关键结论有数据支撑 | 数据+图表+推导三位一体 |
| 图表质量 | 10 | 图表可读、无空白占位 | 达到论文发表水平 |

## Process

### Step 1: Collect All Outputs

Read all workspace files:
1. `mm-workspace/01_analysis.json` — extract the problem text and analysis
2. `mm-workspace/02_modeling.json` — extract task list and modeling approach
3. All `mm-workspace/03_task_*.json` files — extract results, answers, verification status
4. List all files in `mm-workspace/charts/` directory

### Step 2: Dispatch Independent Review Subagent

Use the Agent tool to dispatch a general-purpose subagent with the following prompt:

```
你是一名资深的数学建模竞赛评审专家。请对以下完整的建模结果进行全局质量审查，按维度量化评分。

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

## 评分标准（百分制，加权求和）

| 维度 | 权重 | 60分线 | 满分要求 |
|------|------|--------|---------|
| 结果一致性 | 20 | 各任务结果无直接矛盾 | 跨任务数值和结论完全自洽 |
| 数值可信度 | 20 | 核心数值无重大错误 | 所有数值有据可查 |
| 需求覆盖度 | 20 | 所有子问题有回答 | 每个子问题有定量结论+图表 |
| 模型连贯性 | 15 | 方法选择无明显矛盾 | 方法故事线完整通顺 |
| 论据充分性 | 15 | 关键结论有数据支撑 | 数据+图表+推导三位一体 |
| 图表质量 | 10 | 图表可读、无空白占位 | 达到论文发表水平 |

通过线：80 分
硬性否决：任意维度 < 10 分 → 总分封顶 59

### 各维度评分要点

#### 1. 结果一致性（Cross-Task Consistency）
- Task 1 得出"A 方案最优"，Task 3 排序中 A 排第二？
- Task 1 输出的数值范围与 Task 2 输入假设不匹配？
- 不同任务对同一变量的定义或取值不一致？

#### 2. 数值可信度（Numerical Credibility）
- 量级错误（如人口 10^15）？
- 符号错误（如成本为负）？
- 百分比/概率超出 [0,1]？
- 关键参数是否有数据支撑？

#### 3. 需求覆盖度（Requirement Coverage）
- 对照赛题原文逐条检查
- 每个子问题是否有数值结论（非仅定性描述）
- 要求的图表是否都已生成

#### 4. 模型连贯性（Model Coherence）
- 方法选择有矛盾？（如前假设线性后用非线性）
- 各任务方法形成完整故事线？
- 假设体系一致？

#### 5. 论据充分性（Evidence Sufficiency）
- 核心结论是否只靠定性论述？
- 图表是否清晰展示关键结果？
- 灵敏度分析是否充分？

#### 6. 图表质量（Chart & Figure Quality）
- 空白图片、占位符、生成失败？
- 轴标签、标题、图例完整准确？
- 配色黑白可辨识？
- 图表类型适合数据？
- 有结论性标题？
- 分辨率足够？

## 输出格式

严格按以下 JSON 格式输出，不要有多余文字：
```json
{
  "scores": {
    "cross_task_consistency": {"score": 0-100, "note": "具体说明"},
    "numerical_credibility": {"score": 0-100, "note": "具体说明"},
    "requirement_coverage": {"score": 0-100, "note": "具体说明"},
    "model_coherence": {"score": 0-100, "note": "具体说明"},
    "evidence_sufficiency": {"score": 0-100, "note": "具体说明"},
    "chart_figure_quality": {"score": 0-100, "note": "具体说明"}
  },
  "total": 加权总分,
  "improvement_directions": ["改进方向1", "改进方向2"],
  "rework_list": [
    {
      "task_id": 2,
      "reason": "具体问题描述",
      "improvement_direction": "改进方向"
    }
  ],
  "fatal_issue": null 或 "具体说明（仅当触发硬性否决时）",
  "summary": "一段话总结评审结论"
}
```

如果 total >= 80，rework_list 为空数组。
如果 total < 80，rework_list 中必须列出需要重修的任务及具体原因。
```

### Step 3: Process Review Results

Receive the subagent's review output. Parse the JSON response.

If **total >= 80** (passed):
- Save review results
- Tag: `cd mm-workspace && git tag review-pass-v{iteration}`

If **60 <= total < 80** (improvable):
- Present scores and rework_list to user
- Ask: "审查得分 {total}/100（通过线 80），以下维度需改进：{improvement_directions}。是否进入第 {iteration+1} 轮迭代重修？"

If **total < 60** (fundamental issues):
- Present as critical failure
- If iteration < 3: ask user whether to retry or accept
- If iteration == 3: pause pipeline, user must decide

### Step 4: Save Review Output

Write to `mm-workspace/03.5_review.json`:

```json
{
  "iteration": 1,
  "total": 82,
  "pass_threshold": 80,
  "passed": true,
  "scores": {
    "cross_task_consistency": {"score": 85, "note": "..."},
    "numerical_credibility": {"score": 90, "note": "..."},
    "requirement_coverage": {"score": 80, "note": "..."},
    "model_coherence": {"score": 75, "note": "..."},
    "evidence_sufficiency": {"score": 70, "note": "..."},
    "chart_figure_quality": {"score": 80, "note": "..."}
  },
  "rework_list": [],
  "summary": "review summary text",
  "stage": "review_complete"
}
```

Then commit: `cd mm-workspace && git add -A && git commit -m "feat(s3.5): global review - iteration {N} (score: {total})"`
