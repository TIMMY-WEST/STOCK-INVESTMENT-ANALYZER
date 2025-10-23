"""D415エラーを自動修正するスクリプト（v3 - 英語ピリオドのみ使用）."""

from pathlib import Path
import re
import subprocess


def get_d415_errors():
    """flake8からD415エラーのリストを取得."""
    result = subprocess.run(
        ["flake8", "--select=D415", "--format=%(path)s:%(row)d"],
        capture_output=True,
        text=True,
    )
    errors = []
    for line in result.stdout.strip().split("\n"):
        if line and "D415" not in line:
            parts = line.split(":")
            if len(parts) >= 2:
                filepath = parts[0]
                lineno = int(parts[1])
                errors.append((filepath, lineno))
    return errors


def fix_docstring_punctuation(filepath, lineno):
    """指定された行のdocstringに英語のピリオドを追加.

    D415は英語のピリオド(.)、疑問符(?)、感嘆符(!)のみを認識する。
    日本語の句読点（。！？）は認識されないため、
    すべてのdocstringに英語のピリオドを追加する。
    """
    path = Path(filepath)
    if not path.exists():
        return False

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if lineno > len(lines):
        return False

    # 該当行（docstring開始行）から処理
    target_line_idx = lineno - 1
    line = lines[target_line_idx]

    # docstringの開始を検出
    if '"""' in line or "'''" in line:
        quote = '"""' if '"""' in line else "'''"

        # 一行docstringの場合（開始と終了が同じ行）
        if line.count(quote) == 2:
            # クォートの間の内容を取得
            match = re.match(
                r"^(\s*)"
                + re.escape(quote)
                + r"(.+?)"
                + re.escape(quote)
                + r"(.*)$",
                line,
            )
            if match:
                indent, content, rest = match.groups()
                content = content.rstrip()
                # 既に英語の句読点がある場合はスキップ
                if content and content[-1] not in ".?!":
                    # 日本語の句読点がある場合は削除してから英語のピリオドを追加
                    if content[-1] in "。！？":
                        content = content[:-1]
                    # 英語のピリオドを追加
                    content = content + "."

                    new_line = f"{indent}{quote}{content}{quote}{rest}"
                    if line.endswith("\n"):
                        new_line += "\n"
                    lines[target_line_idx] = new_line

                    with open(path, "w", encoding="utf-8") as f:
                        f.writelines(lines)
                    return True
        else:
            # 複数行docstringの場合
            # 開始行に内容がある場合（例: """これは説明）
            match = re.match(r"^(\s*)" + re.escape(quote) + r"(.+)$", line)
            if match:
                indent, content = match.groups()
                content = content.rstrip()
                # 既に英語の句読点がある場合はスキップ
                if content and content[-1] not in ".?!":
                    # 日本語の句読点がある場合は削除してから英語のピリオドを追加
                    if content[-1] in "。！？":
                        content = content[:-1]
                    # 英語のピリオドを追加
                    content = content + "."
                    lines[target_line_idx] = f"{indent}{quote}{content}\n"

                    with open(path, "w", encoding="utf-8") as f:
                        f.writelines(lines)
                    return True
            else:
                # 開始行に内容がない場合（例: """  \n 説明）
                # 次の非空行を探す
                for i in range(target_line_idx + 1, len(lines)):
                    next_line = lines[i]
                    next_line_stripped = next_line.strip()

                    # 終了クォートの行は無視
                    if quote in next_line_stripped and (
                        next_line_stripped == quote
                        or next_line_stripped.startswith(quote)
                    ):
                        break

                    # 空行は無視
                    if not next_line_stripped:
                        continue

                    # 最初の非空行を発見
                    content = next_line.rstrip()
                    if content and content[-1] not in ".?!":
                        # 日本語の句読点がある場合は削除してから英語のピリオドを追加
                        if content[-1] in "。！？":
                            content = content[:-1]
                        # 英語のピリオドを追加
                        lines[i] = content + ".\n"

                        with open(path, "w", encoding="utf-8") as f:
                            f.writelines(lines)
                        return True
                    break

    return False


def main():
    """メイン処理."""
    print("D415エラーを取得中...")
    errors = get_d415_errors()
    print(f"検出されたD415エラー: {len(errors)}件")

    if not errors:
        print("修正の必要なエラーはありません!")
        return

    fixed_count = 0
    failed_files = []

    for filepath, lineno in errors:
        if fix_docstring_punctuation(filepath, lineno):
            fixed_count += 1
            if fixed_count % 50 == 0:
                print(f"修正済み: {fixed_count}件")
        else:
            failed_files.append((filepath, lineno))

    print(f"\n修正完了:")
    print(f"  成功: {fixed_count}件")
    print(f"  失敗: {len(failed_files)}件")

    if failed_files and len(failed_files) <= 10:
        print("\n失敗したファイル:")
        for filepath, lineno in failed_files:
            print(f"  {filepath}:{lineno}")

    # 修正後のエラー確認
    print("\n修正後のD415エラーを確認中...")
    remaining_errors = get_d415_errors()
    print(f"残りのD415エラー: {len(remaining_errors)}件")

    if remaining_errors and len(remaining_errors) <= 5:
        print("\n残りのエラー:")
        for filepath, lineno in remaining_errors[:5]:
            print(f"  {filepath}:{lineno}")


if __name__ == "__main__":
    main()
