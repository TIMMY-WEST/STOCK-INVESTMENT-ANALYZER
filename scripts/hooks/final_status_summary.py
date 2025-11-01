#!/usr/bin/env python3
"""Print final commit status summary.

- Console output: English
- Comments: Japanese

Read status file (.git/.precommit_status.json) and print each check result
and "Final commit status: <SUCCESS/FAIL>". If any recorded check failed,
exit non-zero so pre-commit shows this hook as Failed.

Additionally, detect whether files were modified (auto-fix applied) during
pre-commit by checking working tree changes via `git diff --name-only` and
mark the commit as FAIL in that case as well.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
STATUS_FILE = REPO_ROOT / ".git" / ".precommit_status.json"


def get_modified_files() -> list[str]:
    """Return list of modified files in working tree.

    pre-commit のフックによる自動修正が入った場合、作業ツリーに変更が残る。
    それを `git diff --name-only` で検出して、最終サマリーに反映する。
    """
    try:
        proc = subprocess.run(
            ["git", "diff", "--name-only"],
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            return []
        files = [
            line.strip() for line in proc.stdout.splitlines() if line.strip()
        ]
        return files
    except Exception:
        return []


def main() -> int:
    final = "UNKNOWN"
    checks = []
    failed_overall = False
    if STATUS_FILE.exists():
        try:
            with STATUS_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            failed_overall = bool(data.get("failed"))
            checks = data.get("checks", [])
        except Exception:
            # ステータスファイルが壊れているなどの場合は安全側で失敗扱い
            failed_overall = True
    # 自動修正による変更検出
    modified_files = get_modified_files()
    if modified_files:
        failed_overall = True

    final = "FAIL" if failed_overall else "SUCCESS"

    print("\n=== Commit Status Summary ===")
    if checks:
        for c in checks:
            name = c.get("name", "?")
            passed = c.get("passed")
            state = "PASS" if passed else "FAIL"
            print(f"- {name}: {state}")
    # 自動修正の有無を表示
    if modified_files:
        count = len(modified_files)
        print(f"- Auto-fixes detected: {count} file(s) modified")
        # 多すぎる場合は一覧を省略
        if count <= 10:
            for fn in modified_files:
                print(f"  * {fn}")
    print(f"Final commit status: {final}")
    # 失敗が一つでもあれば、非ゼロ終了にしてpre-commitのヘッダーにFailedを表示させる
    return 1 if failed_overall else 0


if __name__ == "__main__":
    sys.exit(main())
