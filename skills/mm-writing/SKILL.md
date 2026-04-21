---
name: mm-writing
description: >
  Stage 4 of the mathematical modeling pipeline. Generates LaTeX paper source
  from all workspace outputs, compiles to PDF. Supports multiple competition
  templates. Invoked by the math-modeling skill during Stage 4.
  Do not invoke directly.
version: 0.2.0
---

# Stage 4: Paper Generation (LaTeX → PDF)

## Purpose

Generate a complete competition paper in LaTeX from all workspace outputs, then compile to PDF.

## Input

- `mm-workspace/01_analysis.json` — problem analysis
- `mm-workspace/02_modeling.json` — modeling solution and tasks
- `mm-workspace/03_task_{id}.json` — all task outputs
- `mm-workspace/04_abstract.json` — generated abstract
- `mm-workspace/charts/` — all figures
- `mm-workspace/data/` — result data files

## Competition Template System

Templates are stored in `references/templates/`. Each template is a directory containing:
- `main.tex` — main document file with placeholder markers
- `refs.bib` — BibTeX reference file (if applicable)
- Any style files (`.cls`, `.sty`, `.bst`)

### Available Templates

| Template ID | Competition | Language | Description |
|-------------|-------------|----------|-------------|
| `mcm` | MCM/ICM | English | 美赛官方格式 |
| `cumcm` | CUMCM | Chinese | 国赛官方格式 |
| `generic` | Any | Configurable | 通用格式 |

If the user's competition type is detected, use the corresponding template. Otherwise use `generic`.

**Template extensibility**: Users can add custom templates by creating a new directory under `references/templates/` with a `main.tex` file.

## Process

### Step 1: Generate Abstract

Load `references/abstract_guide.md` and follow its instructions:
1. Read all `03_task_{id}.json` files
2. Extract key results, methods, and innovations
3. Generate abstract following the guide's structure
4. Save to `mm-workspace/04_abstract.json`

### Step 2: Load Template

Read the appropriate template from `references/templates/{template_id}/main.tex`.
If no template exists for the detected competition, use `references/templates/generic/main.tex`.

### Step 3: Generate Paper Sections

For each section of the paper, generate LaTeX content based on workspace outputs:

#### Abstract Section
- Read from `mm-workspace/04_abstract.json`
- Insert into the abstract placeholder

#### Problem Restatement
- Based on `mm-workspace/raw_problem.txt`
- Rephrase in own words, 1-2 paragraphs

#### Assumptions
- Extract from `02_modeling.json` modeling_solution
- Format as numbered list with justifications

#### Notation / Symbol Table
- Extract all variables from task formulas
- Generate a LaTeX table: `Symbol | Description | Unit`

#### Model Establishment (per task)
For each task in `dag_order`:
- Read `03_task_{id}.json`
- Extract: formulas, modeling_process
- Generate LaTeX section with:
  - Method description
  - Mathematical formulations (already in LaTeX)
  - Model assumptions specific to this sub-problem

#### Model Solution
For each task:
- Describe the solution approach
- Reference the code implementation
- Present key numerical results in tables/figures

#### Results and Analysis
For each task:
- Read result_interpretation and answer
- Present results with figures (reference charts)
- Discuss findings and implications

#### Sensitivity Analysis
- Read the sensitivity analysis task output (if exists)
- Present parameter perturbation results
- Discuss model robustness

#### Model Evaluation
- Strengths of the model
- Weaknesses and limitations
- Possible improvements

#### References
- Collect method references from HMML retrieval
- Format as BibTeX entries
- Generate bibliography

### Step 4: Integrate Figures

For each figure in `mm-workspace/charts/`:
1. Copy or symlink to `mm-workspace/05_paper/figures/`
2. Generate LaTeX `\includegraphics` command
3. Add appropriate caption and label

### Step 5: Assemble and Save

Write the complete paper to `mm-workspace/05_paper/main.tex`:
- Replace template placeholders with generated content
- Ensure all `\ref{}` and `\label{}` are consistent
- Ensure all figures are referenced
- Write BibTeX file to `mm-workspace/05_paper/refs.bib` (if applicable)

### Step 6: Compile to PDF

```bash
cd mm-workspace/05_paper && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

If compilation fails:
1. Read the error log
2. Fix LaTeX syntax issues (common: unescaped special characters, missing packages)
3. Retry up to 3 times

### Step 7: Present to User

Display:
- Paper structure overview (sections and page estimate)
- Abstract text
- All figures included
- PDF file path
- Any compilation warnings

Then ask: "论文已生成。是否需要修改？"

## Output Structure

```
mm-workspace/05_paper/
├── main.tex          # 完整 LaTeX 源码
├── main.pdf          # 编译后的 PDF
├── main.aux          # LaTeX 辅助文件
├── refs.bib          # 参考文献（如适用）
├── figures/          # 论文图片
│   ├── task_1_fig1.png
│   └── ...
└── sections/         # 各章节源码（可选，用于调试）
    ├── abstract.tex
    ├── problem.tex
    └── ...
```
