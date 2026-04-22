---
name: mm-modeling
description: >
  Stage 2 of the mathematical modeling pipeline. Performs high-level modeling,
  problem decomposition into subtasks, and DAG dependency analysis. Uses
  Actor-Critic with percent-based scoring. Invoked by the math-modeling skill
  during Stage 2. Do not invoke directly.
version: 0.4.2
---

# Stage 2: Modeling & Decomposition

## Purpose

Design a comprehensive mathematical modeling solution, decompose it into manageable subtasks, and establish task dependencies via DAG analysis.

## Input

Read `mm-workspace/01_analysis.json` for the problem analysis results.

## Process

### Step 1: High-Level Modeling (Actor-Critic, 自适应 1-3 轮, 通过线 75 分)

Load `references/actor_critic.md` for the scoring criteria.

#### Actor: Generate Modeling Solution

Design a complete modeling solution covering:
- **Assumption system**: Clear, justified assumptions
- **Variable definitions**: All variables, parameters, and constants
- **Constraints**: Mathematical constraints from the problem
- **Key equations**: Governing equations and relationships
- **Solution strategy**: Analytical, numerical, or simulation approach
- **Validation plan**: How to verify the model's correctness
- **Validation independence declaration**: For each model, explicitly state:
  1. Whether the data/information used for validation is independent from estimation
  2. If not independent (e.g., constraint satisfaction methods), what additional means ensure validation effectiveness (held-out test set, different data sources, different evaluation metrics)
  3. Constraint satisfaction methods must use information different from constraint conditions for validation
- **Fit quality warning thresholds**: For each estimation model, preset:
  - Which metrics below what threshold require switching to alternatives
  - Example: R² < 0.3 → switch to non-parametric methods or add features
  - Example: optimization objective difference between alternatives < 5% → need additional criteria
  - These thresholds will be written into `02_modeling.json` for Task solving stage reference
- **Innovation**: Novel formulations or extensions

Write as structured modeling solution: use numbered lists for assumptions, tables for variable definitions, and numbered LaTeX equations. Use coherent paragraphs for reasoning.

#### Critic: Score the Modeling Solution (Independent Subagent)

Use the Agent tool to dispatch an independent subagent for the Critic role. The subagent must NOT inherit the Actor's reasoning context — it only receives the Actor's final output.

Dispatch an Agent with the following prompt structure:
```
你是一名严格的数学建模评审专家（Critic 角色）。请对以下建模方案按维度量化评分。

## 评分标准（百分制，加权求和）

| 维度 | 权重 | 60分线 | 满分要求 |
|------|------|--------|---------|
| 可行性 | 20 | 方案可用现有工具和数据实现 | 实现路径清晰，无技术盲区 |
| 方法匹配度 | 20 | 方法与问题类型对应 | 方法选择有对比论证 |
| 任务分解 | 20 | 任务覆盖所有子问题，无重叠 | DAG依赖合理，粒度适中 |
| 验证有效性 | 10 | 验证方案不含循环论证 | 验证方法与估计方法独立 |
| 假设体系 | 15 | 假设之间不矛盾 | 假设体系自洽且有论证 |
| 创新性 | 15 | 有合理的模型设计 | 有原创性贡献 |

通过线：75 分
硬性否决：可行性 < 15 分 → 总分封顶 59。验证有效性 < 10 分 → 总分封顶 59。

## 问题背景
{Insert brief problem description, 1-2 paragraphs}

## 被审查的建模方案
{Insert Actor's complete modeling solution}

## 输出要求
严格按以下 JSON 格式输出，不要有多余文字：
```json
{
  "scores": {
    "feasibility": {"score": 0-100, "note": "具体说明"},
    "method_match": {"score": 0-100, "note": "具体说明"},
    "task_decomposition": {"score": 0-100, "note": "具体说明"},
    "validation_effectiveness": {"score": 0-100, "note": "具体说明"},
    "assumption_system": {"score": 0-100, "note": "具体说明"},
    "innovation": {"score": 0-100, "note": "具体说明"}
  },
  "total": 加权总分,
  "improvement_directions": ["具体改进方向1", "改进方向2"],
  "fatal_issue": null 或 "具体说明（仅当触发硬性否决时填写）"
}
```
```

Receive the Critic scores and process:
- If `total >= 75`: Accept the modeling solution, proceed to Step 2
- If `total < 75` and round < 3: Run Improvement, then repeat Actor → Critic
- If `total < 60` and round == 3: Pause pipeline, present to user for decision

#### Improvement: Refine the Modeling Solution

Produce an improved version addressing all `improvement_directions`. Complete standalone document.

### Step 2: Problem Decomposition

Split the modeling solution into 3-6 subtasks (default: 5, including sensitivity analysis).

**Decomposition principles:**
- Each subtask addresses a distinct aspect of the overall problem
- Subtasks should map to the competition's question structure when possible
- Each subtask has clear objectives, methods, and expected outputs
- No redundancy between subtasks
- All aspects of the modeling solution are covered
- **The last subtask should be a sensitivity analysis / robustness testing task** that depends on all model-building tasks, testing parameter perturbations, assumption variations, and result stability

For each subtask, provide:
- **ID**: Sequential number (1, 2, 3, ...)
- **Description**: Detailed task description (one paragraph, comprehensive)
- **Method**: Expected modeling/approach method
- **Expected output**: What the task should produce

**Refinement**: After initial decomposition, refine each subtask description to be more specific and actionable. Ensure each can be understood independently.

### Step 3: DAG Construction

Analyze dependencies between subtasks:

1. **Identify dependencies** for each task:
   - Data dependencies (output of task A feeds into task B)
   - Method dependencies (task B builds on task A's framework)
   - Computational dependencies (task B needs task A's numerical results)

2. **Build adjacency list**:
   ```
   {
     "1": [],
     "2": ["1"],
     "3": ["1"],
     "4": ["2", "3"]
   }
   ```

3. **Compute topological order**: Determine the execution sequence.
   For the example above: [1, 2, 3, 4] (tasks 2 and 3 can be parallel)

4. **Generate dependency analysis**: For each task, write a brief paragraph explaining its dependencies.

### Step 4: Save Output

Write to `mm-workspace/02_modeling.json`:

```json
{
  "modeling_solution": "final improved modeling solution text",
  "tasks": [
    {
      "id": 1,
      "description": "detailed task description",
      "method": "expected method",
      "expected_output": "what this task produces",
      "dependencies": []
    }
  ],
  "dag_order": [1, 2, 3, 4],
  "dependency_analysis": ["task 1 dependency analysis...", "task 2 dependency analysis..."],
  "stage": "modeling_complete"
}
```

Then commit: `cd mm-workspace && git add -A && git commit -m "feat(s2): modeling and decomposition complete"`

### Step 5: Present to User

Display:
- Summary of the modeling approach
- Task decomposition overview (list each task with its objective)
- Dependency graph and execution order
- Which tasks can be parallelized

Then ask: "建模方案和任务分解完成。是否需要修改？确认后开始逐任务求解。"
