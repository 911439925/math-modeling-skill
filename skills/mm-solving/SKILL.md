---
name: mm-solving
description: >
  Stage 3 of the mathematical modeling pipeline. Solves each subtask by retrieving
  modeling methods from HMML, generating formulas, writing and executing Python code,
  and interpreting results. Invoked by the math-modeling skill during Stage 3.
  Do not invoke directly.
version: 0.1.0
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

Write as a cohesive paragraph. Include dependency context.

### Step 3: HMML Method Retrieval

Load `references/hmml.md` and retrieve the top-6 most relevant modeling methods:

1. Read the HMML knowledge base
2. Based on the task description and analysis, identify relevant methods by evaluating:
   - **Assumptions**: Do the method's assumptions match the problem characteristics?
   - **Structure**: Does the mathematical framework fit the problem's logic?
   - **Variables**: Is the method compatible with the variable types in the problem?
   - **Dynamics**: Does it handle the temporal/evolutionary aspects?
   - **Solvability**: Is it computationally feasible?
3. Select the top-6 methods and format them as:
   ```
   **Method Name**: Brief description and why it's relevant
   ```

### Step 4: Formula Generation (Actor-Critic, 1 round)

#### Actor: Generate Mathematical Formulas

Based on the retrieved methods and task analysis:
- Define all variables, constants, parameters
- Derive the governing equations
- State assumptions and boundary conditions
- Ensure dimensional consistency
- Use LaTeX notation for all mathematical expressions
- Write as continuous prose with inline formulas

#### Critic: Evaluate Formulas

Critically examine:
- **Accuracy**: Are formulas mathematically sound?
- **Innovation**: Is the approach novel or merely standard?
- **Applicability**: Can these formulas be implemented computationally?
- **Completeness**: Are all necessary constraints and conditions included?

Do NOT provide suggestions.

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

### Step 10: Present to User

Display:
- Task summary and approach used
- Key results and findings
- Generated files (code, data, charts)
- Any issues encountered

Then ask: "任务 {id} 完成。是否继续下一个任务？"

## Parallel Execution

When multiple tasks have no mutual dependencies (can run simultaneously according to the DAG), you MAY use the Agent tool to solve them in parallel. However:
- Each parallel agent works in its own context
- Ensure no file conflicts (each task writes to its own files)
- Wait for all parallel tasks to complete before proceeding to dependent tasks
