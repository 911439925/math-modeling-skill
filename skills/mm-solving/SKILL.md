---
name: mm-solving
description: >
  Stage 3 of the mathematical modeling pipeline. Solves each subtask by retrieving
  modeling methods from HMML, generating formulas, writing and executing Python code,
  and interpreting results. Invoked by the math-modeling skill during Stage 3.
  Do not invoke directly.
version: 0.2.0
---

# Stage 3: Task Solving

## Purpose

Solve each subtask by: retrieving relevant modeling methods from the HMML knowledge base, generating mathematical formulas, writing executable Python code, and interpreting the results.

## Input

- `mm-workspace/01_analysis.json` — problem analysis
- `mm-workspace/02_modeling.json` — modeling solution and task decomposition

## Process (per task, in DAG topological order)

For each task ID in the `dag_order` from `02_modeling.json`:

### Step 1: Load Dependencies

Read any prerequisite task outputs:
- For each task ID in the current task's `dependencies` list
- Read `mm-workspace/03_task_{dep_id}.json`
- Extract: task description, modeling method, code structure, result interpretation, output files
- Build a dependency prompt that summarizes what previous tasks have accomplished

### Step 2: Task Analysis

Analyze the current task in context:
- Its objectives and scope within the larger problem
- How it builds on (or differs from) prerequisite tasks
- Specific data, algorithms, or models required
- Challenges and assumptions

**Special case**: If this task is the final "sensitivity analysis / robustness testing" task, go to [Sensitivity Analysis Special Process](#sensitivity-analysis-special-process) instead of the regular steps below.

Write as a cohesive paragraph. Include dependency context.

### Step 3: HMML Method Retrieval

Load `references/hmml_index.md` first. Based on the task type, load only the relevant domain file(s):
- Optimization/scheduling problems → `references/hmml_or.md` or `references/hmml_optimization.md`
- Classification/clustering/regression → `references/hmml_ml.md`
- Forecasting/time-series → `references/hmml_prediction.md`
- Evaluation/ranking → `references/hmml_evaluation.md`
- Mixed problems → load 2 domain files maximum

Retrieve the top-6 most relevant modeling methods by evaluating:
- **Assumptions**: Do the method's assumptions match the problem characteristics?
- **Structure**: Does the mathematical framework fit the problem's logic?
- **Variables**: Is the method compatible with the variable types in the problem?
- **Dynamics**: Does it handle the temporal/evolutionary aspects?
- **Solvability**: Is it computationally feasible?

Select the top-6 methods and format as:
```
**Method Name**: Brief description and why it's relevant
```

After selecting top-6 methods, check the "常见方法组合模式" table in `hmml_index.md`. If any combination pattern matches the current task and its dependencies, note it for the formula generation step.

### Step 4: Formula Generation (Actor-Critic, 1 round)

Load `references/actor_critic.md` for the Actor-Critic mechanism guide.

#### Actor: Generate Mathematical Formulas

Based on the retrieved methods and task analysis:
- Define all variables, constants, parameters (use tables)
- Derive the governing equations (use numbered LaTeX)
- State assumptions and boundary conditions (use numbered list)
- Ensure dimensional consistency
- Use structured format: tables for variables, numbered equations, paragraphs for reasoning

#### Critic: Evaluate Formulas

Critically examine:
- **Accuracy**: Are formulas mathematically sound?
- **Innovation**: Is the approach novel or merely standard?
- **Applicability**: Can these formulas be implemented computationally?
- **Completeness**: Are all necessary constraints and conditions included?

Must provide specific improvement directions (not just "this is wrong").

#### Improvement: Refine Formulas

Produce improved formulas addressing all critiques.

### Step 5: Modeling Process Elaboration

Based on the formulas, write a detailed step-by-step modeling process:
- How to apply each formula
- Computational procedure
- Parameter estimation approach
- Expected intermediate results
- This should be detailed enough to guide code implementation

### Step 6: Code Generation and Execution

#### 6a: Generate Python Code

Load `references/code_templates.md` for code structure guidelines.

Write Python code that:
- Loads input data or reads prerequisite task output files
- Implements the modeling process step by step
- Saves intermediate results to `mm-workspace/data/`
- Generates visualizations if appropriate (save to `mm-workspace/charts/`)
- Prints detailed output for result interpretation

Follow the standard code structure from the template reference.

Save the code to `mm-workspace/code/task_{id}.py`.

#### 6b: Execute the Code

Run the code using Bash:
```bash
cd {working_directory} && python mm-workspace/code/task_{id}.py
```

#### 6c: Debug if Needed (max 3 rounds)

If the execution fails:
1. Read the full error traceback
2. Identify the root cause
3. Fix the code in `mm-workspace/code/task_{id}.py`
4. Re-execute
5. Repeat up to 3 times

If all 3 rounds fail, mark the task as failed but continue with the next task.

### Step 7: Result Interpretation

Based on the code execution results (or formula derivation if no code):
- Summarize the key findings
- Provide numerical results with context
- Explain what the results mean for the problem
- Compare with expected outcomes if applicable

### Step 8: Answer Generation

Craft a comprehensive answer that:
- States the primary conclusions
- Evaluates model effectiveness and reliability
- Discusses potential biases and limitations
- Explores broader implications
- Is distinct from the result interpretation (adds analysis, not repetition)

### Step 9: Save Task Output

Write to `mm-workspace/03_task_{id}.json`:

```json
{
  "task_id": 1,
  "analysis": "task analysis text",
  "retrieved_methods": "top-6 methods text",
  "formulas": "mathematical formulas",
  "modeling_process": "detailed modeling process",
  "code_path": "mm-workspace/code/task_1.py",
  "execution_success": true,
  "execution_result": "key output summary (truncated if too long)",
  "result_interpretation": "result analysis text",
  "answer": "comprehensive answer text",
  "charts": ["mm-workspace/charts/task_1_fig1.png"],
  "output_files": ["mm-workspace/data/task_1_result.csv"],
  "stage": "task_complete"
}
```

### Step 10: Present and Continue

Display:
- Task summary and approach used
- Key results and findings
- Generated files (code, data, charts)
- Any issues encountered

Then **automatically proceed** to the next task. Only pause if:
- The task execution failed and needs user guidance
- The user explicitly interrupts

## Sensitivity Analysis Special Process

If the current task is a sensitivity analysis / robustness testing task, follow this adapted process:

1. **Identify core models**: Read all prerequisite task outputs and identify the core model parameters and assumptions.

2. **Design sensitivity tests**:
   - **Parameter perturbation**: Vary key parameters by ±5%, ±10%, ±20% and observe output changes
   - **Assumption variation**: Relax or change one assumption at a time and evaluate impact
   - **Data noise**: Add random noise to input data and check result stability

3. **Write sensitivity analysis code** following the standard code template, with:
   - A loop over perturbation levels
   - Comparison of perturbed results vs baseline
   - Calculation of sensitivity indices (e.g., relative change in output / relative change in input)
   - Visualization: tornado diagrams, spider plots, or heatmaps

4. **Interpret results**: Determine which parameters/assumptions the model is most sensitive to, and discuss implications for model reliability.

5. Save output as `mm-workspace/03_task_{id}.json` with `is_sensitivity_analysis: true`.

## Parallel Execution

When multiple tasks have no mutual dependencies (can run simultaneously according to the DAG), you MAY use the Agent tool to solve them in parallel. However:
- Each parallel agent works in its own context
- Ensure no file conflicts (each task writes to its own files)
- Wait for all parallel tasks to complete before proceeding to dependent tasks
