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
from character.core.schema import CharacterSheet

OUTPUT_DIR = Path("output")


def save_characters(characters: list[CharacterSheet], label: str) -> list[Path]:
    """バリデーション済みキャラクターをYAMLファイルとして保存する"""
    OUTPUT_DIR.mkdir(exist_ok=True)

    safe_label = "".join(c for c in label[:20] if c.isalnum() or c in "_ ").strip().replace(" ", "_")
    save_dir = OUTPUT_DIR / safe_label
    save_dir.mkdir(exist_ok=True)

    saved = []
    for i, char in enumerate(characters, 1):
        safe_name = "".join(c for c in char.name if c.isalnum() or c in "_-").strip() or f"char_{i}"
        path = save_dir / f"{i:02d}_{safe_name}.yaml"
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(char.model_dump(exclude_none=True), f, allow_unicode=True,
                      default_flow_style=False, sort_keys=False)
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
        except RuntimeError as e:
            # CLI・タイムアウト・コマンド未導入などの実行エラー
            print(f"\nエラー: {e}")
            continue
        except ValueError as e:
            # パース失敗・バリデーション全滅など
            print(f"\n生成失敗: {e}")
            continue

        saved_paths = save_characters(characters, instruction)

        print(f"\n{len(characters)}人のキャラクターを生成しました")
        print("-" * 40)
        for path, char in zip(saved_paths, characters):
            age = f"{char.age}歳" if char.age else ""
            occ = char.occupation or ""
            print(f"  {path.name}  {char.name}（{age}）{occ}")

        print(f"\n保存先: {saved_paths[0].parent}/")
        print()


if __name__ == "__main__":
    main()
