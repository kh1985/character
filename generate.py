"""
使い方:
  python generate.py                          # デフォルトサンプル
  python generate.py characters/sample.yaml   # ファイル指定
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from character.core.generator import from_yaml

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "characters/sample.yaml"
    prompt = from_yaml(path)

    print("=" * 60)
    print("生成されたシステムプロンプト")
    print("=" * 60)
    print(prompt)
    print("=" * 60)
    print(f"\n文字数: {len(prompt)} 文字")
    print(f"トークン概算: 約{len(prompt) // 2} tokens（日本語）")

if __name__ == "__main__":
    main()
