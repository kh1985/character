"""
マスターAI：自然言語の指示からキャラクターYAMLを一括生成する
"""

from __future__ import annotations

import re
import subprocess
import yaml

# ── マスターAIへの指示（内部プロンプト）──────────────────────────────
MASTER_SYSTEM_PROMPT = """あなたはキャラクター設計の専門家です。
ユーザーの指示を受け取り、キャラクターのYAMLファイルを生成します。

## 出力フォーマット

キャラクターごとに以下のYAMLブロックで出力してください。
複数人の場合は ```yaml ブロックを繰り返してください。

```yaml
name: （名前）
age: （年齢・数値）
occupation: （職業・立場）

tone:
  rule: "語尾・口調のルールを1文で"
  examples:
    - user: "最近どう？"
      char: "（キャラらしい返答）"
    - user: "ありがとう"
      char: "（キャラらしい返答）"
    - user: "それって本当？"
      char: "（キャラらしい返答）"

personality:
  - "性格を行動・反応で描写（形容詞だけにしない）"
  - "（もう1つ）"
  - "（もう1つ）"

forbidden:
  - "やってはいけない言動を1つ"
  - "（もう1つ）"

context:
  backstory: "生い立ち・背景を2〜3文で"
  current_situation: "現在どういう場面・状況にいるか"
```

## 重要なルール
- personality は形容詞ではなく行動で書く（例: 「明るい」→「誰かに話しかけられると必ず先に笑う」）
- tone.examples はそのキャラが実際に言いそうなセリフにする
- 複数人の場合、全員の個性がかぶらないようにする
- 名前は日本人らしいものにする"""


def generate_characters(instruction: str) -> list[dict]:
    """
    自然言語の指示からキャラクターのリストを生成して返す。
    claude CLI を使って生成するため、APIキー設定不要。

    Args:
        instruction: 「ギャルゲーのテストプレイヤーを10人、現代日本人男性で」など

    Returns:
        キャラクターのdictリスト
    """
    full_prompt = f"{MASTER_SYSTEM_PROMPT}\n\n---\n\n{instruction}"

    # CLAUDECODE環境変数があるとネスト禁止エラーになるため除外して実行
    env = {k: v for k, v in __import__("os").environ.items() if k != "CLAUDECODE"}

    result = subprocess.run(
        ["claude", "-p", full_prompt],
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )

    if result.returncode != 0:
        raise RuntimeError(f"claude CLI エラー:\n{result.stderr}")

    return _parse_yaml_blocks(result.stdout)


def _parse_yaml_blocks(text: str) -> list[dict]:
    """レスポンスからYAMLブロックを抽出してパースする"""
    # ```yaml ... ``` ブロックを全部抽出
    blocks = re.findall(r"```yaml\s*(.*?)```", text, re.DOTALL)

    if not blocks:
        # ブロックがなければ --- 区切りで分割を試みる
        blocks = [b.strip() for b in text.split("---") if b.strip()]

    characters = []
    for block in blocks:
        try:
            parsed = yaml.safe_load(block)
            if isinstance(parsed, dict) and "name" in parsed:
                characters.append(parsed)
        except yaml.YAMLError:
            continue

    return characters
