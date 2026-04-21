# MM-Skill 维护指南

## 仓库结构

```
math-modeling-skill/
├── .claude-plugin/
│   └── marketplace.json          ← Marketplace 清单（一般不改）
├── plugins/
│   └── math-modeling/
│       ├── .claude-plugin/
│       │   └── plugin.json       ← 插件元信息（name/description/version）
│       └── skills/               ← 所有 skill 文件
│           ├── math-modeling/    ← 主控 skill + references
│           ├── math-model-command/
│           ├── mm-analysis/
│           ├── mm-modeling/
│           ├── mm-solving/
│           ├── mm-review/
│           └── mm-writing/
├── README.md
├── MAINTENANCE.md                ← 本文件
└── deploy.ps1                    ← 旧版部署脚本（marketplace 安装后不再需要）
```

## 修改现有 Skill

1. 编辑 `plugins/math-modeling/skills/<skill-name>/SKILL.md`
2. 如果是主控 skill，同步更新 `plugin.json` 中的 `version`
3. 提交并推送：

```bash
cd E:/MM_agent/MM-Agent/math-modeling
git add plugins/math-modeling/skills/<skill-name>/SKILL.md
git commit -m "fix(<skill>): 简述修改内容"
git push origin master
```

4. 用户端更新：

```
/plugin marketplace update mm-skill-market
/plugin install math-modeling@mm-skill-market
```

## 新增 Skill

1. 创建目录和文件：

```
plugins/math-modeling/skills/<new-skill>/SKILL.md
```

2. SKILL.md 开头必须有 YAML frontmatter（Claude Code 靠它识别 skill）：

```yaml
---
name: <new-skill>
description: 触发描述，写清楚什么时候激活这个 skill
version: 0.3.0
---

# Skill 标题

...具体指令...
```

3. 提交：

```bash
git add plugins/math-modeling/skills/<new-skill>/
git commit -m "feat: add <new-skill> skill"
git push origin master
```

无需修改 `marketplace.json` 或 `plugin.json`——Claude Code 自动发现 `skills/` 下的新目录。

## 新增 Reference 文件

放到 `plugins/math-modeling/skills/math-modeling/references/` 下即可：

```bash
git add plugins/math-modeling/skills/math-modeling/references/<file>
git commit -m "docs: add <file> reference"
git push origin master
```

## 版本号规范

遵循 semver，在 `plugin.json` 中维护：

- **主版本**（x.0.0）：不兼容的结构变更（如合并/拆分 skill）
- **次版本**（0.x.0）：新增 skill 或新功能（如 v0.3.0 加了 mm-review）
- **修订号**（0.0.x）：文字修正、bug 修复

修改后：

```bash
# 更新 plugin.json 中的 version 字段
git add plugins/math-modeling/.claude-plugin/plugin.json
git commit -m "chore: bump version to x.y.z"
git push origin master
```

## Commit 规范

| 前缀 | 用途 | 示例 |
|------|------|------|
| `feat` | 新增 skill 或功能 | `feat: add mm-sensitivity skill` |
| `fix` | 修复 skill 逻辑错误 | `fix(mm-solving): correct verification step` |
| `docs` | 文档或 reference 更新 | `docs: update hmml_index methods` |
| `refactor` | 重构 skill 结构 | `refactor(mm-analysis): simplify critic flow` |
| `chore` | 版本号、配置等 | `chore: bump version to 0.4.0` |

## 常见维护场景

### 场景 1：修复 skill 中的流程问题

```bash
# 1. 编辑 SKILL.md
vim plugins/math-modeling/skills/mm-solving/SKILL.md

# 2. 提交
git add -A && git commit -m "fix(mm-solving): 具体修复内容"
git push origin master

# 3. 用户更新
/plugin marketplace update mm-skill-market
```

### 场景 2：新增一个建模方法到 HMML 知识库

```bash
# 1. 创建或编辑 references 文件
vim plugins/math-modeling/skills/math-modeling/references/hmml_statistics.md

# 2. 更新索引（如果需要）
vim plugins/math-modeling/skills/math-modeling/references/hmml_index.md

# 3. 提交
git add -A && git commit -m "docs: add statistics methods to HMML"
git push origin master
```

### 场景 3：新增一种竞赛模板

```bash
# 1. 创建模板目录
mkdir -p plugins/math-modeling/skills/math-modeling/references/templates/mathorcup
vim plugins/math-modeling/skills/math-modeling/references/templates/mathorcup/main.tex

# 2. 提交
git add -A && git commit -m "feat: add MathorCup LaTeX template"
git push origin master
```

### 场景 4：大版本升级（涉及多个 skill）

```bash
# 1. 逐个修改涉及的 skill 文件
# 2. 更新 plugin.json 的 version
# 3. 一次性提交
git add -A && git commit -m "feat: v0.4.0 - 具体变更摘要"
git push origin master
```

## 注意事项

- **不要改 `marketplace.json`** 除非要改 marketplace 名称或增加新插件
- **SKILL.md 的 YAML frontmatter 是必须的**，`name` 和 `description` 字段影响 skill 的识别和触发
- **推送后用户不会自动更新**，需要用户主动执行 `/plugin marketplace update`
- **私有仓库用户**需要设置 `GITHUB_TOKEN` 环境变量才能安装和更新
- **本地测试**：推送前可以用 `/plugin marketplace add ./E:/MM_agent/MM-Agent/math-modeling` 测试本地版本
