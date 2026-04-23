#!/usr/bin/env python3
"""
cross_task_consistency.py — 跨任务一致性快速检查

用法:
    python cross_task_consistency.py <workspace_dir> [--current-task <id>]

参数:
    workspace_dir      mm-workspace 目录路径
    --current-task N   当前刚完成的 task ID（仅检查该 task 与已完成 task 的一致性）

退出码:
    0  无警告
    1  存在一致性警告（不阻塞流程，仅报告）
"""

import json
import os
import re
import sys


def load_task_jsons(workspace_dir):
    """加载所有 03_task_*.json"""
    tasks = {}
    pattern = re.compile(r"03_task_(\d+)\.json$")
    for fname in os.listdir(workspace_dir):
        m = pattern.match(fname)
        if m:
            tid = int(m.group(1))
            fpath = os.path.join(workspace_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    tasks[tid] = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"  [WARN] Cannot load {fname}: {e}")
    return tasks


def load_dag(workspace_dir):
    """从 02_modeling.json 加载 DAG 依赖"""
    modeling_path = os.path.join(workspace_dir, "02_modeling.json")
    if not os.path.isfile(modeling_path):
        return {}, []
    with open(modeling_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    deps = {}
    for t in data.get("tasks", []):
        deps[t["id"]] = t.get("dependencies", [])
    return deps, data.get("dag_order", sorted(deps.keys()))


def extract_numeric_metrics(obj, prefix=""):
    """从 JSON 对象中递归提取数值型指标（排除元数据字段）"""
    # 不参与比较的元数据字段
    SKIP_KEYS = {"task_id", "execution_success", "stage", "id"}
    metrics = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in SKIP_KEYS:
                continue
            full_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                metrics[full_key] = v
            elif isinstance(v, dict):
                metrics.update(extract_numeric_metrics(v, full_key))
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        metrics.update(extract_numeric_metrics(item, f"{full_key}[{i}]"))
    return metrics


def check_metric_conflicts(current_task, all_tasks, current_id):
    """检查 1: 指标名称冲突"""
    warnings = []
    current_metrics = extract_numeric_metrics(current_task)
    # 扁平化：只用最后一层 key 做匹配
    current_flat = {k.split(".")[-1]: (k, v) for k, v in current_metrics.items()}

    for tid, tdata in all_tasks.items():
        if tid == current_id:
            continue
        other_metrics = extract_numeric_metrics(tdata)
        other_flat = {k.split(".")[-1]: (k, v) for k, v in other_metrics.items()}

        # 同名指标检查
        common_keys = set(current_flat.keys()) & set(other_flat.keys())
        for key in common_keys:
            cur_full, cur_val = current_flat[key]
            oth_full, oth_val = other_flat[key]

            if cur_val == 0 and oth_val == 0:
                continue

            # 量级差异 > 10x
            if cur_val != 0 and oth_val != 0:
                ratio = max(abs(cur_val), abs(oth_val)) / max(min(abs(cur_val), abs(oth_val)), 1e-10)
                if ratio > 10:
                    warnings.append({
                        "type": "metric_magnitude_conflict",
                        "detail": f'指标 "{key}" 在 Task {current_id} 值为 {cur_val:.4g}, '
                                  f'在 Task {tid} 值为 {oth_val:.4g} (差异 {ratio:.1f}x)',
                        "severity": "warning"
                    })

    return warnings


def check_value_chain(current_task, all_tasks, current_id, dependencies):
    """检查 2: 数值传递链"""
    warnings = []
    deps = dependencies.get(current_id, [])
    if not deps:
        return warnings

    # 从当前 task 提取所有数值
    current_metrics = extract_numeric_metrics(current_task)

    # 从前置 task 提取所有数值
    for dep_id in deps:
        dep_task = all_tasks.get(dep_id)
        if not dep_task:
            continue
        dep_metrics = extract_numeric_metrics(dep_task)

        # 检查：前置 task 的输出值是否出现在当前 task 的输入假设中
        # 简化策略：寻找名称相似且数值接近的指标
        dep_flat = {k.split(".")[-1]: (k, v) for k, v in dep_metrics.items()}
        cur_flat = {k.split(".")[-1]: (k, v) for k, v in current_metrics.items()}

        common_keys = set(dep_flat.keys()) & set(cur_flat.keys())
        for key in common_keys:
            dep_full, dep_val = dep_flat[key]
            cur_full, cur_val = cur_flat[key]

            if dep_val == 0 and cur_val == 0:
                continue
            if dep_val == 0 or cur_val == 0:
                continue

            # 检查偏差是否 > 5%
            diff_pct = abs(cur_val - dep_val) / max(abs(dep_val), 1e-10) * 100
            if diff_pct > 5:
                warnings.append({
                    "type": "value_chain_mismatch",
                    "detail": f'传递链偏差: "{key}" 前置 Task {dep_id} 输出 {dep_val:.4g}, '
                              f'当前 Task {current_id} 使用 {cur_val:.4g} (偏差 {diff_pct:.1f}%)',
                    "severity": "warning"
                })

    return warnings


def check_json_schema_basic(task_data, task_id):
    """检查 3: JSON 格式完整性（快速版）"""
    warnings = []
    required = ["task_id", "execution_success", "answer", "verification", "stage"]
    for field in required:
        if field not in task_data:
            warnings.append({
                "type": "schema_missing_field",
                "detail": f"Task {task_id}: 缺少必填字段 '{field}'",
                "severity": "error"
            })
    return warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python cross_task_consistency.py <workspace_dir> [--current-task <id>]")
        sys.exit(1)

    workspace_dir = sys.argv[1]
    current_task_id = None
    if "--current-task" in sys.argv:
        idx = sys.argv.index("--current-task")
        if idx + 1 < len(sys.argv):
            current_task_id = int(sys.argv[idx + 1])

    if not os.path.isdir(workspace_dir):
        print(f"ERROR: Directory not found: {workspace_dir}")
        sys.exit(1)

    print(f"=== Cross-Task Consistency Check ===")
    print(f"  Workspace: {workspace_dir}")
    if current_task_id is not None:
        print(f"  Current task: {current_task_id}")
    print()

    # 加载数据
    tasks = load_task_jsons(workspace_dir)
    dependencies, dag_order = load_dag(workspace_dir)

    if not tasks:
        print("  No task JSON files found.")
        sys.exit(0)

    print(f"  Loaded {len(tasks)} task(s): {sorted(tasks.keys())}")
    print()

    all_warnings = []

    # 确定检查范围
    if current_task_id is not None:
        check_ids = [current_task_id]
    else:
        check_ids = sorted(tasks.keys())

    for tid in check_ids:
        if tid not in tasks:
            print(f"  [SKIP] Task {tid} JSON not found")
            continue

        tdata = tasks[tid]
        print(f"--- Task {tid} ---")

        # 检查 1: JSON 基本完整性
        w1 = check_json_schema_basic(tdata, tid)
        for w in w1:
            tag = w["severity"].upper()
            print(f'  [{tag}] {w["detail"]}')
        all_warnings.extend(w1)

        # 检查 2: 指标名称冲突
        w2 = check_metric_conflicts(tdata, tasks, tid)
        for w in w2:
            print(f'  [WARN] {w["detail"]}')
        all_warnings.extend(w2)

        # 检查 3: 数值传递链
        w3 = check_value_chain(tdata, tasks, tid, dependencies)
        for w in w3:
            print(f'  [WARN] {w["detail"]}')
        all_warnings.extend(w3)

        if not (w1 + w2 + w3):
            print("  [OK] No issues found")

        print()

    # 汇总
    error_count = sum(1 for w in all_warnings if w["severity"] == "error")
    warn_count = sum(1 for w in all_warnings if w["severity"] == "warning")

    print("--- Summary ---")
    print(f"  Errors:   {error_count}")
    print(f"  Warnings: {warn_count}")

    # 输出 known_issues 格式（供 pipeline_state.json 使用）
    if all_warnings:
        print("\n--- known_issues (JSON) ---")
        issues_json = []
        for w in all_warnings:
            issues_json.append({
                "source_task": current_task_id or "all",
                "type": w["type"],
                "detail": w["detail"]
            })
        print(json.dumps(issues_json, ensure_ascii=False, indent=2))

    if error_count > 0:
        print(f"\nResult: HAS ERRORS ({error_count})")
        sys.exit(1)
    elif warn_count > 0:
        print(f"\nResult: HAS WARNINGS ({warn_count})")
        sys.exit(1)  # warnings 也不阻塞，但返回非零以便主代理感知
    else:
        print("\nResult: ALL CLEAR")
        sys.exit(0)


if __name__ == "__main__":
    main()
