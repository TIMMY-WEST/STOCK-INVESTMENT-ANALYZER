#!/usr/bin/env python3
"""Wrapper to run checks and print commit status.

- Console output is in English (repo policy).
- Source comments are in Japanese (repo policy).

Flow:
1) Run specified check (black/isort/flake8/mypy/complexity/coverage).
2) On failure, save status file and optionally auto-fix.
3) After each check, print "Commit status after <check>: <SUCCESS/FAIL>".
4) Return non-zero if the check fails.

Status file: .git/.precommit_status.json
This stores per-check pass/fail and overall failed state.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List


# リポジトリルートを特定（このスクリプトは scripts/hooks/ 配下に置かれる想定）
REPO_ROOT = Path(__file__).resolve().parents[2]
STATUS_FILE = REPO_ROOT / ".git" / ".precommit_status.json"


def load_status() -> Dict[str, Any]:
    # ステータスファイルを読み込み、存在しなければ初期化
    if STATUS_FILE.exists():
        try:
            with STATUS_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            # 最低限の構造保証
            if (
                not isinstance(data, dict)
                or "checks" not in data
                or "failed" not in data
            ):
                raise ValueError("invalid status json")
            return data
        except Exception:
            pass
    return {"checks": [], "failed": False}


def save_status(status: Dict[str, Any]) -> None:
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with STATUS_FILE.open("w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False, indent=2)


def set_check_result(status: Dict[str, Any], name: str, passed: bool) -> None:
    """Update or append check result by name."""
    checks = status.setdefault("checks", [])
    for c in checks:
        if c.get("name") == name:
            c["passed"] = passed
            return
    checks.append({"name": name, "passed": passed})


def print_commit_status_after(check_name: str, status: Dict[str, Any]) -> None:
    # 現時点で一つでも失敗があれば、このコミットは失敗扱い
    overall = "FAIL" if status.get("failed") else "SUCCESS"
    print(f"Commit status after {check_name}: {overall}")


def run(cmd: List[str]) -> int:
    # 標準出力/標準エラーはそのまま継承して表示
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except FileNotFoundError:
        print(f"Command not found: {' '.join(cmd)}")
        return 127


def run_black(
    args: List[str], files: List[str], status: Dict[str, Any]
) -> int:
    # まず --check で判定し、必要なら実フォーマットを実施
    cmd_check = [sys.executable, "-m", "black", "--check", *args, *files]
    rc_check = run(cmd_check)
    if rc_check != 0:
        # 自動修正を実施
        cmd_fix = [sys.executable, "-m", "black", *args, *files]
        _ = run(cmd_fix)
        set_check_result(status, "black", False)
        status["failed"] = True
        save_status(status)
        print_commit_status_after("black", status)
        # blackが修正した場合はコミット失敗（pre-commit標準挙動に合わせる）
        return 1
    else:
        set_check_result(status, "black", True)
        save_status(status)
        print_commit_status_after("black", status)
        return 0


def run_isort(
    args: List[str], files: List[str], status: Dict[str, Any]
) -> int:
    cmd_check = [sys.executable, "-m", "isort", "--check-only", *args, *files]
    rc_check = run(cmd_check)
    if rc_check != 0:
        # 自動修正
        cmd_fix = [sys.executable, "-m", "isort", *args, *files]
        _ = run(cmd_fix)
        set_check_result(status, "isort", False)
        status["failed"] = True
        save_status(status)
        print_commit_status_after("isort", status)
        return 1
    else:
        set_check_result(status, "isort", True)
        save_status(status)
        print_commit_status_after("isort", status)
        return 0


def run_flake8(
    args: List[str], files: List[str], status: Dict[str, Any]
) -> int:
    cmd = [sys.executable, "-m", "flake8", *args, *files]
    rc = run(cmd)
    set_check_result(status, "flake8", rc == 0)
    if rc != 0:
        status["failed"] = True
    save_status(status)
    print_commit_status_after("flake8", status)
    return rc


def run_mypy(args: List[str], files: List[str], status: Dict[str, Any]) -> int:
    # mypyにもターゲット（ディレクトリ/ファイル）を渡す
    cmd = [sys.executable, "-m", "mypy", *args, *files]
    rc = run(cmd)
    set_check_result(status, "mypy", rc == 0)
    if rc != 0:
        status["failed"] = True
    save_status(status)
    print_commit_status_after("mypy", status)
    return rc


def run_complexity(
    args: List[str], files: List[str], status: Dict[str, Any]
) -> int:
    # 複雑度チェック（flake8のC901を使用）
    cmd = [sys.executable, "-m", "flake8", *args, *files]
    rc = run(cmd)
    set_check_result(status, "complexity", rc == 0)
    if rc != 0:
        status["failed"] = True
    save_status(status)
    print_commit_status_after("complexity", status)
    return rc


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run check and print commit status"
    )
    parser.add_argument(
        "--check",
        required=True,
        choices=["black", "isort", "flake8", "mypy", "complexity"],
        help="Which check to run",
    )
    # 追加の引数は未知のオプションも許容して取得する
    known_args, extra = parser.parse_known_args()

    # ステータスを読み込み（最初の黒フック時にリセット）
    status = load_status()
    if known_args.check == "black":
        status = {"checks": [], "failed": False}
        save_status(status)

    # pre-commitからの未知引数にはツールオプションとファイルパスが混在
    files: List[str] = []
    tool_args: List[str] = []
    for token in extra:
        # ファイルと思われるものとオプションの分離
        p = Path(token)
        if p.exists():
            files.append(token)
        else:
            tool_args.append(token)

    if known_args.check == "black":
        return run_black(tool_args, files, status)
    elif known_args.check == "isort":
        return run_isort(tool_args, files, status)
    elif known_args.check == "flake8":
        return run_flake8(tool_args, files, status)
    elif known_args.check == "mypy":
        # mypyにもファイル/ディレクトリを渡す
        return run_mypy(tool_args, files, status)
    elif known_args.check == "complexity":
        return run_complexity(tool_args, files, status)
    else:
        print(f"Unsupported check: {known_args.check}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
