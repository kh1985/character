"""
キャラクター生成システム

使い方:
  python main.py

起動後、自然言語で指示を入力するだけ。
"""

import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from character.core.master import generate_characters


OUTPUT_DIR = Path("output")


def save_characters(characters: list[dict], label: str) -> list[Path]:
    """生成したキャラクターをYAMLファイルとして保存する"""
    OUTPUT_DIR.mkdir(exist_ok=True)

    # 保存先サブフォルダ（指示の先頭20文字をフォルダ名に）
    safe_label = "".join(c for c in label[:20] if c.isalnum() or c in "_ ").strip().replace(" ", "_")
    save_dir = OUTPUT_DIR / safe_label
    save_dir.mkdir(exist_ok=True)

    saved = []
    for i, char in enumerate(characters, 1):
        name = char.get("name", f"character_{i}")
        # ファイル名に使えない文字を除去
        safe_name = "".join(c for c in name if c.isalnum() or c in "_-").strip() or f"char_{i}"
        path = save_dir / f"{i:02d}_{safe_name}.yaml"
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(char, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        saved.append(path)

    return saved


def main():
    print("=" * 50)
    print("  キャラクター生成システム")
    print("  終了: Ctrl+C")
    print("=" * 50)
    print()

    while True:
        try:
            instruction = input("指示 > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n終了します")
            break

        if not instruction:
            continue

        print(f"\n生成中...")

        try:
            characters = generate_characters(instruction)
        except Exception as e:
            print(f"エラー: {e}")
            print("ANTHROPIC_API_KEY が設定されているか確認してください")
            continue

        if not characters:
            print("キャラクターを生成できませんでした。指示を変えてみてください。")
            continue

        saved_paths = save_characters(characters, instruction)

        print(f"\n{len(characters)}人のキャラクターを生成しました")
        print("-" * 40)
        for path in saved_paths:
            # 保存したファイルから名前だけ読んで表示
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            name = data.get("name", "?")
            age = data.get("age", "?")
            occ = data.get("occupation", "")
            print(f"  {path.name}  {name}（{age}歳）{occ}")

        print(f"\n保存先: {saved_paths[0].parent}/")
        print()


if __name__ == "__main__":
    main()
