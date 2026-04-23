#!/usr/bin/env python3
"""
validate_task_output.py — 校验 03_task_{id}.json 输出 schema 合规性

用法:
    python validate_task_output.py <task_json_path> [--fix]

参数:
    task_json_path    03_task_{id}.json 文件路径
    --fix             尝试自动回填可推断的字段

退出码:
    0  全部通过
    1  存在 ERROR 级别缺失（不可自动回填）
    2  存在 WARNING（schema 不完整但可继续）
"""

import json
import os
import sys


# ── 字段定义 ──────────────────────────────────────────────────
# level: ERROR = 核心字段, 不可自动回填
#        BACKFILL = 可从其他字段推断
#        WARN = 建议存在但非阻塞

FIELDS = [
    {"name": "task_id",              "type": "int",    "required": True,  "level": "ERROR",
     "rule": "Must equal expected task ID"},
    {"name": "execution_success",    "type": "bool",   "required": True,  "level": "ERROR",
     "rule": "Must exist"},
    {"name": "stage",                "type": "str",    "required": True,  "level": "BACKFILL",
     "rule": 'Must be "task_complete"', "default": "task_complete"},
    {"name": "verification",         "type": "dict",   "required": True,  "level": "ERROR",
     "rule": "Must exist, with passed (bool) and checks (list, len>=4)"},
    {"name": "answer",               "type": "str",    "required": True,  "level": "BACKFILL",
     "rule": "Length > 50 chars", "min_length": 50},
    {"name": "charts",               "type": "list",   "required": True,  "level": "WARN",
     "rule": "Must exist (can be empty)", "default": []},
    {"name": "result_interpretation","type": "str",    "required": True,  "level": "BACKFILL",
     "rule": "Must exist"},
    {"name": "code_path",            "type": "str",    "required": True,  "level": "ERROR",
     "rule": "Must point to existing file"},
    {"name": "retrieved_methods",    "type": "str",    "required": True,  "level": "WARN",
     "rule": "HMML retrieval result", "default": "N/A"},
    {"name": "formulas",             "type": "str",    "required": True,  "level": "BACKFILL",
     "rule": "Mathematical formulas"},
    {"name": "modeling_process",     "type": "str",    "required": True,  "level": "BACKFILL",
     "rule": "Modeling process description"},
    {"name": "analysis",             "type": "str",    "required": False, "level": "WARN",
     "rule": "Task analysis"},
    {"name": "execution_result",     "type": "str",    "required": False, "level": "WARN",
     "rule": "Execution result summary"},
    {"name": "output_files",         "type": "list",   "required": False, "level": "WARN",
     "rule": "Output file list"},
]


def get_nested(data, path):
    """获取嵌套字段，如 verification.passed"""
    keys = path.split(".")
    obj = data
    for k in keys:
        if isinstance(obj, dict) and k in obj:
            obj = obj[k]
        else:
            return None
    return obj


def set_nested(data, path, value):
    """设置嵌套字段"""
    keys = path.split(".")
    obj = data
    for k in keys[:-1]:
        if k not in obj:
            obj[k] = {}
        obj = obj[k]
    obj[keys[-1]] = value


def validate_field(data, field, task_json_dir):
    """校验单个字段，返回 (passed, level, message)"""
    name = field["name"]
    value = get_nested(data, name)

    # 字段不存在
    if value is None:
        if not field["required"]:
            return True, "INFO", f"{name}: optional field missing"
        return False, field["level"], f"{name}: MISSING"

    # 类型检查
    expected_type = field["type"]
    type_map = {"int": int, "bool": bool, "str": str, "list": list, "dict": dict}
    py_type = type_map[expected_type]
    # bool 是 int 的子类，需要特殊处理
    if expected_type == "int" and isinstance(value, bool):
        return False, "ERROR", f"{name}: expected int, got bool"
    if not isinstance(value, py_type):
        return False, "ERROR", f"{name}: expected {expected_type}, got {type(value).__name__}"

    # 特定规则
    rule = field.get("rule", "")

    if name == "task_id":
        pass  # task_id 值的校验在调用方处理

    if name == "stage" and value != "task_complete":
        return False, "BACKFILL", f'{name}: expected "task_complete", got "{value}"'

    if name == "verification":
        v_passed = value.get("passed")
        v_checks = value.get("checks", [])
        issues = []
        if not isinstance(v_passed, bool):
            issues.append("verification.passed should be bool")
        if not isinstance(v_checks, list):
            issues.append("verification.checks should be list")
        elif len(v_checks) < 4:
            issues.append(f"verification.checks length {len(v_checks)} < 4")
        if issues:
            return False, "ERROR", f"{name}: {'; '.join(issues)}"

    if "min_length" in field and len(str(value)) < field["min_length"]:
        return False, "BACKFILL", \
            f"{name}: length {len(str(value))} < {field['min_length']}"

    if name == "code_path":
        if not os.path.isabs(value):
            full_path = os.path.join(task_json_dir, value)
        else:
            full_path = value
        if not os.path.isfile(full_path):
            return False, "ERROR", f"{name}: file not found: {value}"

    return True, "OK", f"{name}: OK"


def try_backfill(data, field, task_json_dir):
    """尝试从其他字段回填"""
    name = field["name"]

    # 有默认值
    if "default" in field:
        set_nested(data, name, field["default"])
        return True

    # 从其他字段推断
    backfill_map = {
        "stage": "task_complete",
        "answer": data.get("result_interpretation", ""),
        "result_interpretation": data.get("answer", ""),
        "formulas": data.get("modeling_process", ""),
        "modeling_process": data.get("formulas", data.get("analysis", "")),
    }

    if name in backfill_map:
        source = backfill_map[name]
        if source:  # 非空
            set_nested(data, name, source)
            return True

    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_task_output.py <task_json_path> [--fix]")
        sys.exit(1)

    json_path = sys.argv[1]
    fix_mode = "--fix" in sys.argv

    if not os.path.isfile(json_path):
        print(f"ERROR: File not found: {json_path}")
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    task_json_dir = os.path.dirname(os.path.abspath(json_path))

    # 从文件名推断期望的 task_id
    basename = os.path.basename(json_path)
    expected_task_id = None
    import re
    m = re.search(r"task_(\d+)", basename)
    if m:
        expected_task_id = int(m.group(1))

    print(f"=== Schema Validation: {basename} ===\n")

    errors = []
    warnings = []
    backfilled = []

    for field in FIELDS:
        passed, level, msg = validate_field(data, field, task_json_dir)

        # 额外检查 task_id 值
        if field["name"] == "task_id" and passed and expected_task_id is not None:
            if data.get("task_id") != expected_task_id:
                passed = False
                level = "ERROR"
                msg = f"task_id: expected {expected_task_id}, got {data.get('task_id')}"

        if passed:
            print(f"  [OK]  {msg}")
        else:
            # 尝试 backfill
            if fix_mode and level == "BACKFILL":
                if try_backfill(data, field, task_json_dir):
                    print(f"  [FIX] {msg} → backfilled")
                    backfilled.append(field["name"])
                    continue

            print(f"  [{level}] {msg}")
            if level == "ERROR":
                errors.append(msg)
            elif level in ("BACKFILL", "WARN"):
                warnings.append(msg)

    # 汇总
    print(f"\n--- Summary ---")
    print(f"  Errors:    {len(errors)}")
    print(f"  Warnings:  {len(warnings)}")
    if fix_mode and backfilled:
        print(f"  Backfilled: {len(backfilled)} ({', '.join(backfilled)})")

    # 如果 fix 模式下有回填，保存文件
    if fix_mode and (backfilled or warnings):
        data["_schema_validated"] = True
        if errors:
            data["_schema_incomplete"] = True
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n  Updated: {json_path}")

    if errors:
        print(f"\n  Result: FAIL ({len(errors)} error(s))")
        sys.exit(1)
    elif warnings:
        print(f"\n  Result: PASS WITH WARNINGS ({len(warnings)} warning(s))")
        sys.exit(2)
    else:
        print(f"\n  Result: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
