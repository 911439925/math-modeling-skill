# MM-Skill: Claude Code 通用数学建模插件

[English](README.md)

一个面向 **所有主流数学建模竞赛** 的 Claude Code 全流水线技能插件。

> **当前版本: v0.4.4** — 流水线状态机、Schema 强制校验、自动化验证脚本。

## 支持的竞赛

| 竞赛 | 缩写 | 时长 | 备注 |
|------|------|------|------|
| 美国大学生数学建模竞赛 | MCM | 4 天 | 英文论文 |
| 美国大学生交叉学科建模竞赛 | ICM | 4 天 | 英文论文 |
| 全国大学生数学建模竞赛 | CUMCM | 3 天 | 中文论文 |
| MathorCup 高校数学建模挑战赛 | MathorCup | 4 天 | 中文论文 |
| 深圳杯数学建模挑战赛 | 深圳杯 | ~2 周 | 中文论文 |
| 其他建模比赛 | — | — | LaTeX 模板可扩展 |

## 安装

### 方式一: Claude Code Marketplace（推荐）

```bash
# 添加 marketplace
/plugin marketplace add 911439925/math-modeling-skill

# 安装插件
/plugin install math-modeling@mm-skill-market
```

私有仓库需先设置 `GITHUB_TOKEN` 环境变量：
```bash
export GITHUB_TOKEN=ghp_your_token_here
```

### 方式二: Git 克隆

```bash
# 克隆到 Claude Code skills 目录
git clone https://github.com/911439925/math-modeling-skill.git ~/.claude/skills/math-modeling-plugin

# Windows PowerShell
git clone https://github.com/911439925/math-modeling-skill.git "$env:USERPROFILE\.claude\skills\math-modeling-plugin"
```

### 更新

Marketplace 用户:
```bash
/plugin marketplace update mm-skill-market
/plugin install math-modeling@mm-skill-market
```

Git 克隆用户:
```bash
cd ~/.claude/skills/math-modeling-plugin && git pull
```

## 功能特性

- **问题分析**: Actor-Critic 自我改进的深度分析（独立 Critic 子代理）
- **建模与分解**: 高层建模方案、任务拆分（3-6 个子任务）、DAG 调度
- **任务求解**: HMML 方法检索（98 种方法，5 个领域）、公式生成、Python 代码执行、结果验证
- **全局质量审查**: 独立 6 维度审查，支持迭代重修（最多 3 轮，80 分通过线）
- **灵敏度分析**: 系统性灵敏度和鲁棒性测试（REQUIRED/RECOMMENDED/OPTIONAL 优先级）
- **论文生成**: LaTeX 源码生成，支持竞赛专属模板（MCM/CUMCM/generic）→ PDF
- **流水线状态机**: `pipeline_state.json` 强制阶段转换——任何阶段不可跳过
- **Schema 验证**: 自动化任务输出校验（`validate_task_output.py`），支持自动回填
- **跨任务一致性**: 自动化指标冲突和数值传递链检查（`cross_task_consistency.py`）
- **Git 版本管理**: 自动化 workspace 版本控制，每阶段 commit + 迭代 tag

## 使用方法

### 启动流水线

```
/math-model path/to/problem.pdf
```

或直接描述问题：

```
/math-model 2026年美赛C题
```

### 流水线阶段

```
初始化 → Stage 1 → Stage 2 → Stage 3 → Stage 3.5 → [迭代?] → Stage 4 → 最终
            ↓          ↓          ↓(自动)    ↓(强制)                  ↓
         [审查]     [审查]    逐任务     全局审查               LaTeX→PDF
         [暂停]     [暂停]    +验证      +重修循环               [暂停]
```

| 阶段 | Skill | 描述 | 是否暂停 |
|------|-------|------|---------|
| 初始化 | math-model-command | Workspace 初始化、git init、问题提取、状态机初始化 | 否 |
| 1 | mm-analysis | 问题分析 + Actor-Critic（独立 Critic，75 分通过线） | 是 |
| 2 | mm-modeling | 建模 + 任务分解 + DAG（75 分通过线） | 是 |
| 3 | mm-solving | 逐任务：HMML → 公式 → 代码 → schema 验证 → 验证 | 否 |
| 3.5 | mm-review | 全局质量审查（独立子代理，80 分通过线，最多 3 轮迭代） | 重修时暂停 |
| 4 | mm-writing | LaTeX 论文生成 → PDF（需 Stage 3.5 通过） | 是 |

### 质量门控

| 门控 | 机制 | 阈值 |
|------|------|------|
| Stage 1 Actor-Critic | 独立 Critic 子代理为分析评分 | 75/100 |
| Stage 2 Actor-Critic | 独立 Critic 子代理为建模评分 | 75/100 |
| 逐任务验证 | 独立验证子代理检查每个任务结果 | Pass/Fail |
| Schema 校验 | `validate_task_output.py` 检查 JSON 必填字段 | 所有必填字段存在 |
| 跨任务一致性 | `cross_task_consistency.py` 检查指标冲突 + 传递链 | 无冲突 |
| 全局审查 | 独立审查子代理，6 个维度，迭代重修 | 80/100 |
| Stage 4 前置条件 | `pipeline_state.json` 必须 `stage_3_5_passed: true` | 硬性门控 |

### 输出结构

```
mm-workspace/
├── .git/                     # Git 版本历史
├── pipeline_state.json       # 流水线状态机 (v0.4.4)
├── 01_analysis.json          # Stage 1 输出
├── 02_modeling.json          # Stage 2 输出（含 DAG）
├── 03_task_1.json ...        # Stage 3 逐任务输出（含验证结果）
├── 03.5_review.json          # Stage 3.5 全局审查
├── 05_paper/                 # Stage 4 LaTeX 论文
│   ├── main.tex              # LaTeX 主文件
│   ├── main.pdf              # 编译后 PDF
│   ├── sections/             # 论文章节
│   └── figures/              # 论文图片
├── code/                     # 生成的 Python 脚本
├── data/                     # 中间数据文件
└── charts/                   # 生成的可视化图表
```

## 环境要求

- Python 3.10+
- numpy, pandas, scipy, matplotlib, seaborn, scikit-learn, networkx, sympy, openpyxl, statsmodels
- TeX Live 或 MiKTeX（用于论文编译）
- Claude Code（推荐 Claude Opus 4.6+）

## 架构

```
plugins/math-modeling/
├── .claude-plugin/plugin.json     # 插件元信息
├── scripts/                       # 自动化脚本
│   ├── validate_task_output.py    # 任务 JSON schema 校验
│   └── cross_task_consistency.py  # 跨任务一致性检查
├── skills/
│   ├── math-modeling/             # 主控 + 参考资料
│   │   ├── SKILL.md               # 流水线定义、状态机、阶段守卫
│   │   └── references/            # HMML 索引、Actor-Critic 指南、模板等
│   ├── math-model-command/        # /math-model 入口命令
│   ├── mm-analysis/               # Stage 1: 问题分析
│   ├── mm-modeling/               # Stage 2: 建模与分解
│   ├── mm-solving/                # Stage 3: 任务求解（子代理派发）
│   ├── mm-review/                 # Stage 3.5: 全局质量审查
│   └── mm-writing/                # Stage 4: 论文生成
```

### 关键设计决策

| 概念 | 实现 |
|------|------|
| 流水线强制执行 | `pipeline_state.json` 状态机 + 阶段转换守卫 |
| 方法检索 | HMML 知识库（98 种方法，5 个领域），按需加载 |
| 自我改进 | Actor-Critic + 独立 Critic 子代理 + 自适应 1-3 轮迭代 |
| 质量保障 | 逐任务验证子代理 + schema 校验 + 全局审查 |
| 跨任务一致性 | `cross_task_consistency.py` + `known_issues` 通过 dispatch prompt 传递 |
| 错误恢复 | 修复验证循环（最多 1 次重试）+ `_schema_incomplete` 降级标记 |
| 论文生成 | LaTeX 模板（MCM/CUMCM/generic）→ PDF 编译 |

### 参考文献

- [MM-Agent](https://arxiv.org/abs/2505.14148) (NeurIPS 2025) — 核心流水线设计参考

## 更新日志

### v0.4.4
- 新增流水线状态机（`pipeline_state.json`）及阶段转换守卫
- 新增任务输出 schema 校验脚本（`validate_task_output.py`）
- 新增跨任务一致性检查脚本（`cross_task_consistency.py`）
- mm-writing 中 Stage 3.5 前置条件硬性检查（4 项验证）
- 验证结果标准化（嵌入 task JSON 的 `independent_verification` 字段）
- 已知问题通过 dispatch prompt 在子代理间传递
- Git commit/tag 强制执行策略
- 并行调度降级策略（顺序执行亦可）
- 灵敏度分析测试项优先级分级（REQUIRED/RECOMMENDED/OPTIONAL）
- 修复后验证循环（每种问题类型最多 1 次重试）

### v0.4.3
- 强化逐任务验证门控
- 子代理不再执行 git 操作（仅主代理）

### v0.4.2
- MCM C 实践后的方法论严谨性增强

### v0.4.1
- Actor-Critic 百分制评分系统

### v0.4.0
- 子代理派发、独立验证、图表审查、强制 Stage 3.5

## 许可证

CC BY-NC
