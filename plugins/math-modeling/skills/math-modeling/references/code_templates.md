# Python 代码模板规范

## 代码生成原则

1. **可直接执行**：生成的代码必须能立即运行，不缺依赖
2. **中间结果持久化**：所有数据处理步骤保存结果到本地文件（CSV/JSON/pickle）
3. **详细输出**：print/logging 输出关键计算步骤和结果
4. **复用前置任务输出**：优先读取前置任务生成的文件，不重复计算
5. **统一图表风格**：所有图表使用一致的视觉风格

## 标准代码结构

```python
"""
Task {id}: {任务标题}
建模方法: {方法名称}
输入文件: {输入文件路径}
输出文件: {输出文件路径}
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import json
import os

# ============================================================
# 0. 全局配置
# ============================================================
# 中文字体支持
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# 统一图表风格
plt.style.use('seaborn-v0_8-whitegrid')
FIG_DPI = 150
FIG_SIZE = (10, 6)

# ============================================================
# 1. 数据加载
# ============================================================
# 加载原始数据或前置任务输出（支持多种格式）

# CSV
# data = pd.read_csv('{input_path}')

# Excel（支持多 sheet）
# data = pd.read_excel('{input_path}', sheet_name='Sheet1')

# JSON
# with open('{input_path}', 'r', encoding='utf-8') as f:
#     data = json.load(f)

# 前置任务输出
# prev = pd.read_csv('mm-workspace/data/task_{dep_id}_result.csv')

print("数据概览:")
print(data.head())
print(data.describe())
print(f"数据形状: {data.shape}")
print(f"缺失值:\n{data.isnull().sum()}")

# ============================================================
# 2. 数据预处理
# ============================================================
# 根据建模需要进行数据清洗、变换

# ============================================================
# 3. 模型构建与求解
# ============================================================
# 根据建模公式实现模型

# ============================================================
# 4. 结果输出
# ============================================================
# 保存结果
result.to_csv('mm-workspace/data/task_{id}_result.csv', index=False, encoding='utf-8-sig')
print(f"\n结果已保存到 mm-workspace/data/task_{id}_result.csv")
print(result)

# ============================================================
# 4.5 模型质量报告（回归/分类/优化任务必填）
# ============================================================
quality_report = {
    'task_id': {id},
    'model_type': 'regression',  # regression / classification / optimization
    'primary_metric': {
        'name': 'R²',
        'value': round(float(r2_score), 4)
    },
    'baseline': {
        'name': 'mean predictor',
        'value': round(float(baseline_score), 4)
    },
    'improvement_over_baseline': round(float((r2_score - baseline_score) / abs(baseline_score) * 100), 2) if baseline_score != 0 else None,
    'passes_quality_threshold': r2_score >= 0.3,
    'warning': None if r2_score >= 0.3
               else f'R²={r2_score:.3f} < 0.3, 弱拟合，下游结论需降级表述为"关联性"而非"预测性"'
}
print(f"\n{'='*60}")
print("模型质量报告:")
print(json.dumps(quality_report, indent=2, ensure_ascii=False))
print(f"{'='*60}")

# 对于优化任务，额外报告：
if is_optimization:
    opt_report = {
        'optimal_at_boundary': False,  # 检查最优点是否在参数边界上
        'parameter_range_used': str(param_bounds),
        'degenerate_check': 'PASS'  # 检查是否退化为平凡解
    }
    print("优化质量报告:")
    print(json.dumps(opt_report, indent=2, ensure_ascii=False))

# ============================================================
# 5. 可视化（如有需要）
# ============================================================
fig, ax = plt.subplots(figsize=FIG_SIZE)
# 绑图代码
ax.set_xlabel('X Label', fontsize=12)
ax.set_ylabel('Y Label', fontsize=12)
ax.set_title('Title', fontsize=14)
fig.tight_layout()
fig.savefig('mm-workspace/charts/task_{id}_fig1.png', dpi=FIG_DPI, bbox_inches='tight')
plt.close(fig)
print(f"图表已保存到 mm-workspace/charts/task_{id}_fig1.png")
```

## 文件命名规范

| 文件类型 | 路径 |
|----------|------|
| 求解代码 | `mm-workspace/code/task_{id}.py` |
| 中间数据 | `mm-workspace/data/task_{id}_{desc}.csv` |
| 结果图表 | `mm-workspace/charts/task_{id}_fig{n}.png` |

## 错误处理

- 代码执行失败时，读取完整错误信息
- 定位错误行和原因
- 修复后重新执行
- 最多 3 轮调试

## 图表风格规范

竞赛论文中图表需要专业、清晰：
- 使用 `seaborn-v0_8-whitegrid` 风格
- DPI ≥ 150
- 字体大小：标题 14pt，轴标签 12pt，刻度 10pt
- 颜色方案：使用色盲友好的调色板（如 `tab10` 或 `Set2`）
- 保存时使用 `bbox_inches='tight'` 避免裁切
- 每张图使用独立 figure 对象，绘制后 `plt.close(fig)` 防止内存泄漏
