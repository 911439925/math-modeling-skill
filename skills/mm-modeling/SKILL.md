---
name: mm-modeling
description: >
  Stage 2 of the mathematical modeling pipeline. Performs high-level modeling,
  problem decomposition into subtasks, and DAG dependency analysis. Invoked by
  the math-modeling skill during Stage 2. Do not invoke directly.
version: 0.2.0
---

# Stage 2: Modeling & Decomposition

## Purpose

Design a comprehensive mathematical modeling solution, decompose it into manageable subtasks, and establish task dependencies via DAG analysis.

## Input

Read `mm-workspace/01_analysis.json` for the problem analysis results.

## Process

### Step 1: High-Level Modeling (Actor-Critic, 2 rounds)

Load `references/actor_critic.md` for the Actor-Critic mechanism guide.

#### Actor: Generate Modeling Solution

Design a complete modeling solution covering:
- **Assumption system**: Clear, justified assumptions
- **Variable definitions**: All variables, parameters, and constants
- **Constraints**: Mathematical constraints from the problem
- **Key equations**: Governing equations and relationships
- **Solution strategy**: Analytical, numerical, or simulation approach
- **Validation plan**: How to verify the model's correctness
- **Innovation**: Novel formulations or extensions

Write as structured modeling solution: use numbered lists for assumptions, tables for variable definitions, and numbered LaTeX equations. Use coherent paragraphs for reasoning.

#### Critic: Evaluate the Modeling Solution (Independent Subagent)

Use the Agent tool to dispatch an independent subagent for the Critic role. The subagent must NOT inherit the Actor's reasoning context — it only receives the Actor's final output.

Dispatch an Agent with the following prompt structure:
```
你是一名严格的数学建模评审专家（Critic 角色）。请对以下建模方案进行批评。

## 审查标准
- 假设合理性：假设是否有充分的理由支撑？
- 技术匹配度：所选方法是否匹配问题类型？
- 数据兼容性：可用数据能否支持该模型？
- 可计算性：该模型在实际中是否可解？
- 完整性：是否覆盖了所有问题要求？

## 问题背景
{Insert brief problem description, 1-2 paragraphs}

## 被审查的建模方案
{Insert Actor's complete modeling solution}

## 输出要求
1. 逐一指出具体问题（附位置引用）
2. 每个问题给出改进方向（指出方向，不提供完整方案）
3. 最后给出总体评价：是否存在重大问题需要追加一轮
4. 直接输出批评内容，不要有多余的寒暄
```

Receive the Critic feedback and proceed to Improvement.

#### Improvement: Refine the Modeling Solution

Produce an improved version addressing all critiques. Complete standalone document.

**Round 2:** Repeat Critic → Improvement once more.

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
