"""
マスターAI：自然言語の指示からキャラクターYAMLを一括生成する
"""

from __future__ import annotations

import re
import subprocess
import yaml
from pydantic import ValidationError

from character.core.schema import CharacterSheet

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

reactions:
  褒められたとき: "（反応の説明）"
  怒ったとき: "（反応の説明）"

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


def generate_characters(instruction: str) -> list[CharacterSheet]:
    """
    自然言語の指示からキャラクターのリストを生成して返す。

    Returns:
        バリデーション済みの CharacterSheet リスト
    Raises:
        RuntimeError: claude CLI の実行に失敗した場合
        ValueError: 有効なキャラクターが1件も生成できなかった場合
    """
    full_prompt = f"{MASTER_SYSTEM_PROMPT}\n\n---\n\n{instruction}"

    env = {k: v for k, v in __import__("os").environ.items() if k != "CLAUDECODE"}

    try:
        result = subprocess.run(
            ["claude", "-p", full_prompt],
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
    except FileNotFoundError:
        raise RuntimeError("claude コマンドが見つかりません。Claude Code CLIがインストールされているか確認してください。")
    except subprocess.TimeoutExpired:
        raise RuntimeError("生成がタイムアウトしました（120秒）。指示を短くするか、人数を減らして試してください。")

    if result.returncode != 0:
        raise RuntimeError(f"claude CLI の実行に失敗しました:\n{result.stderr}")

    raw_dicts = _parse_yaml_blocks(result.stdout)

    if not raw_dicts:
        raise ValueError("YAMLブロックをひとつも抽出できませんでした。出力を確認してください。")

    # バリデーション：成功分だけ返し、失敗分は警告
    characters: list[CharacterSheet] = []
    for i, d in enumerate(raw_dicts, 1):
        try:
            characters.append(CharacterSheet.from_dict(d))
        except ValidationError as e:
            name = d.get("name", f"#{i}")
            print(f"  ⚠️  [{name}] バリデーション失敗（スキップ）: {e.errors()[0]['msg']}")

    if not characters:
        raise ValueError("有効なキャラクターを1件も生成できませんでした。")

    return characters


def _parse_yaml_blocks(text: str) -> list[dict]:
    """レスポンスから ```yaml ... ``` ブロックを抽出してパースする"""
    blocks = re.findall(r"```yaml\s*(.*?)```", text, re.DOTALL)

    if not blocks:
        blocks = [b.strip() for b in text.split("---") if b.strip()]

    results = []
    for block in blocks:
        try:
            parsed = yaml.safe_load(block)
            if isinstance(parsed, dict) and "name" in parsed:
                results.append(parsed)
        except yaml.YAMLError as e:
            print(f"  ⚠️  YAMLパースエラー（スキップ）: {e}")

    return results
