---
name: mm-analysis
description: >
  Stage 1 of the mathematical modeling pipeline. Performs deep problem analysis
  using Actor-Critic self-improvement. Invoked by the math-modeling skill during
  Stage 1. Do not invoke directly — use /math-model instead.
version: 0.1.0
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

1. Run a Python script to examine the data:
   ```python
   import pandas as pd
   import json

   data = pd.read_csv('path/to/data.csv')  # adjust format as needed
   summary = {
       'shape': list(data.shape),
       'columns': list(data.columns),
       'dtypes': {col: str(dt) for col, dt in data.dtypes.items()},
       'head': data.head(3).to_dict(),
       'describe': data.describe().to_dict(),
       'null_counts': data.isnull().sum().to_dict()
   }
   print(json.dumps(summary, indent=2, default=str))
   ```

2. Generate a concise text summary of the data covering:
   - Number of records and fields
   - Data types and ranges
   - Missing values and anomalies
   - Key statistics

### Step 3: Problem Analysis (Actor-Critic, 2 rounds)

Load `references/actor_critic.md` for the Actor-Critic mechanism guide.

**Round 1:**

#### Actor: Generate Initial Analysis

Produce a deep analysis covering:
- **Core objectives**: What is the model trying to achieve?
- **Implicit assumptions**: What beliefs or constraints are embedded in the problem?
- **Interdependencies**: How do different problem components relate?
- **Hidden complexities**: What challenges arise from component interactions?
- **Temporal/scale considerations**: How might the problem evolve?
- **Alternative perspectives**: Different ways to frame the problem
- **Risks and uncertainties**: Inherent in choosing modeling approaches

Write as continuous prose paragraphs. No Markdown formatting. No bullet points.

#### Critic: Evaluate the Analysis

Critically examine the analysis focusing on:
- **Depth**: Does it go beyond surface observations?
- **Novelty**: Does it offer new insights?
- **Rigor**: Are the steps logically consistent?
- **Context**: Does it consider real-world implications?
- **Data awareness**: Does it fully leverage available data?

Do NOT provide improvement suggestions. Only highlight weaknesses.

#### Improvement: Refine the Analysis

Based on the critique, produce an improved version:
- Address all identified weaknesses
- Do not reference the previous version or its flaws
- Write as a complete, standalone analysis

**Round 2:**

Repeat the Critic → Improvement cycle once more.

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

### Step 5: Present to User

Display a concise summary:
- Problem type and key challenges identified
- Main objectives and assumptions
- Data availability summary
- Key insights from the analysis

Then ask: "问题分析完成。是否需要修改或补充？确认后进入建模阶段。"
