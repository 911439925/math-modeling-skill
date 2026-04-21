---
name: math-model-command
description: "Start the mathematical modeling pipeline. Use when the user types /math-model."
argument-hint: <problem-file-or-description>
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent]
---

# /math-model: Mathematical Modeling Pipeline

Start the full mathematical modeling pipeline.

## Arguments

$ARGUMENTS

This can be:
- A file path to the problem (PDF, image, text)
- A problem description in text
- Empty (if the problem was already provided in conversation)

## Instructions

When this command is invoked:

1. **Parse the input**:
   - If `$ARGUMENTS` is a file path, read the file
   - If `$ARGUMENTS` is text, use it as the problem description
   - If empty, check if a problem was already discussed in conversation

2. **Initialize workspace**:
   ```bash
   mkdir -p mm-workspace/code mm-workspace/data mm-workspace/charts
   ```

3. **Invoke the main skill**: Activate the `math-modeling` skill and follow its workflow starting from Stage 1.

4. **Execute the full pipeline**: Follow the math-modeling skill's stage-by-stage instructions, pausing at each stage for user review.
