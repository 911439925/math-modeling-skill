---
name: mm-analysis
description: >
  Stage 1 of the mathematical modeling pipeline. Performs deep problem analysis
  using Actor-Critic self-improvement with percent-based scoring. Invoked by the
  math-modeling skill during Stage 1. Do not invoke directly — use /math-model instead.
version: 0.4.2
---

# Stage 1: Problem Analysis

## Purpose

Deeply analyze the mathematical modeling problem, understanding its background, objectives, assumptions, constraints, and potential challenges. Use Actor-Critic mechanism to iteratively improve the analysis quality.

## Input

- Problem text (from conversation or file)
- Dataset files (if any, from `mm-workspace/raw_problem.txt` or user-provided paths)

## Process

### Step 1: Problem Extraction

Read the problem and extract structured information:

1. **Background**: The domain, motivation, and context of the problem
2. **Requirements**: Specific questions to answer, constraints to satisfy
3. **Data Available**: List all dataset files and their locations
4. **Addendum**: Any supplementary information, notes, or clarifications

If the problem is in a PDF or image, use the Read tool to extract the content.

### Step 2: Data Summary (if dataset exists)

If the problem includes data files:

1. Determine data format and load appropriately:
   - CSV: `pd.read_csv('path/to/data.csv')`
   - Excel (single or multi-sheet): `pd.read_excel('path/to/data.xlsx', sheet_name=None)`
   - JSON: `pd.read_json('path/to/data.json')`
   - Image-based tables: Note in summary that OCR/extraction is needed

2. Run a Python script to examine the data:
   ```python
   import pandas as pd
   import numpy as np
   import json

   # Adjust loading method based on file type
   data = pd.read_csv('path/to/data.csv')  # or read_excel, read_json

   # Basic summary
   summary = {
       'shape': list(data.shape),
       'columns': list(data.columns),
       'dtypes': {col: str(dt) for col, dt in data.dtypes.items()},
       'head': data.head(3).to_dict(),
       'describe': data.describe().to_dict(),
       'null_counts': data.isnull().sum().to_dict(),
       'null_pct': (data.isnull().sum() / len(data) * 100).to_dict()
   }
   print(json.dumps(summary, indent=2, default=str))

   # Outlier detection (IQR method)
   for col in data.select_dtypes(include=[np.number]).columns:
       Q1, Q3 = data[col].quantile(0.25), data[col].quantile(0.75)
       IQR = Q3 - Q1
       outliers = ((data[col] < Q1 - 1.5*IQR) | (data[col] > Q3 + 1.5*IQR)).sum()
       if outliers > 0:
           print(f"WARNING: {col} has {outliers} potential outliers ({outliers/len(data)*100:.1f}%)")

   # Data quality issues
   for col in data.columns:
       if data[col].isnull().sum() > 0:
           pct = data[col].isnull().sum() / len(data) * 100
           print(f"WARNING: {col} has {pct:.1f}% missing values")
   ```

3. Generate a concise text summary of the data covering:
   - Number of records and fields
   - Data types and ranges
   - Missing values and anomalies
   - Key statistics
   - Potential data quality issues and cleaning suggestions

### Step 3: Problem Analysis (Actor-Critic, 自适应 1-3 轮, 通过线 75 分)

Load `references/actor_critic.md` for the scoring criteria.

#### Actor: Generate Initial Analysis

Produce a deep analysis covering:
- **Core objectives**: What is the model trying to achieve?
- **Implicit assumptions**: What beliefs or constraints are embedded in the problem?
- **Interdependencies**: How do different problem components relate?
- **Hidden complexities**: What challenges arise from component interactions?
- **Temporal/scale considerations**: How might the problem evolve?
- **Alternative perspectives**: Different ways to frame the problem
- **Risks and uncertainties**: Inherent in choosing modeling approaches

Write as structured analysis: use numbered lists for assumptions, tables for variable definitions, and numbered LaTeX for key equations. Use coherent paragraphs for reasoning and discussion.

#### Critic: Score the Analysis (Independent Subagent)

Use the Agent tool to dispatch an independent subagent for the Critic role. The subagent must NOT inherit the Actor's reasoning context — it only receives the Actor's final output.

Dispatch an Agent with the following prompt structure:
```
你是一名严格的数学建模评审专家（Critic 角色）。请对以下问题分析按维度量化评分。

## 评分标准（百分制，加权求和）

| 维度 | 权重 | 60分线 | 满分要求 |
|------|------|--------|---------|
| 需求完整性 | 25 | 所有显式子问题均已识别 | 显式+隐式需求全部挖掘 |
| 深度洞察 | 25 | 超越表面，识别隐含约束 | 发现非常规难点和跨问题关联 |
| 数据感知 | 20 | 数据已加载、缺失值/异常值已报告 | 数据特征深度分析+清洗方案 |
| 假设识别 | 15 | 关键假设已列出 | 假设合理性论证充分 |
| 结构清晰度 | 15 | 分析有结构、可读 | 建模导向明确，直接指导下一阶段 |

通过线：75 分
硬性否决：需求完整性 < 10 分 → 总分封顶 59

## 问题背景
{Insert problem text summary, 1-2 paragraphs}

## 被审查的分析内容
{Insert Actor's complete analysis output}

## 输出要求
严格按以下 JSON 格式输出，不要有多余文字：
```json
{
  "scores": {
    "requirement_completeness": {"score": 0-100, "note": "具体说明"},
    "depth_insight": {"score": 0-100, "note": "具体说明"},
    "data_awareness": {"score": 0-100, "note": "具体说明"},
    "assumption_identification": {"score": 0-100, "note": "具体说明"},
    "structure_clarity": {"score": 0-100, "note": "具体说明"}
  },
  "total": 加权总分,
  "improvement_directions": ["具体改进方向1", "改进方向2"],
  "fatal_issue": null 或 "具体说明（仅当触发硬性否决时填写）"
}
```
```

Receive the Critic scores and process:
- If `total >= 75`: Accept the analysis, proceed to Step 4
- If `total < 75` and round < 3: Run Improvement, then repeat Actor → Critic
- If `total < 60` and round == 3: Pause pipeline, present to user for decision

#### Improvement: Refine the Analysis

Based on Critic's `improvement_directions`, produce an improved version:
- Address all identified weaknesses
- Do not reference the previous version or its flaws
- Write as a complete, standalone analysis

### Step 4: Save Output

Write the final output to `mm-workspace/01_analysis.json`:

```json
{
  "problem_text": "complete problem text",
  "data_summary": "data summary text or empty string",
  "analysis": "final improved analysis text",
  "has_dataset": true,
  "dataset_files": ["file1.csv"],
  "stage": "analysis_complete"
}
```

Use the Write tool to save this file.

Then commit: `cd mm-workspace && git add -A && git commit -m "feat(s1): problem analysis complete"`

### Step 5: Present to User

Display a concise summary:
- Problem type and key challenges identified
- Main objectives and assumptions
- Data availability summary
- Key insights from the analysis

Then ask: "问题分析完成。是否需要修改或补充？确认后进入建模阶段。"
