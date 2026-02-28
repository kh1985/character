"""
キャラクタープロンプトジェネレーター

YAMLで定義されたキャラクターを読み込み、
ブレにくいシステムプロンプトを研究ベースの順序で生成する。

生成順序（研究知見に基づく）:
  1. アイデンティティ宣言
  2. 口調の固定（冒頭に固定）
  3. 性格・振る舞い（行動ベース）
  4. 感情別反応パターン
  5. 会話例（few-shot）← 一番ブレを防ぐ
  6. 背景・状況
  7. 禁止事項（後半に置く）

参考:
  - Lost-in-the-Middle: 重要情報は冒頭か末尾に
  - 制約を冒頭に置くとキャラクター表現が硬直化する
  - Few-shot 3〜5例が最適（RoleLLM, ACL 2024）
  - 500〜700トークンがキャラクター用途の最適帯
"""

from __future__ import annotations

from pathlib import Path
from pydantic import ValidationError
import yaml

from character.core.schema import CharacterSheet


def load_yaml(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def generate(data: dict) -> str:
    """
    キャラクター定義dictからシステムプロンプトを生成する。
    スキーマバリデーションを行い、不正データは例外を出す。
    """
    try:
        char = CharacterSheet.from_dict(data)
    except ValidationError as e:
        raise ValueError(f"キャラクター定義が不正です:\n{e}") from e

    name = char.name
    lines: list[str] = []

    # ── Block 1: アイデンティティ宣言 ──────────────
    age_str = f"{char.age}歳" if char.age else ""
    occ_str = f"{char.occupation}の" if char.occupation else ""
    age_occ = f"（{age_str}）" if age_str else ""
    lines.append(f"あなたは{occ_str}{name}{age_occ}です。{name}として返答してください。")
    lines.append(f"「演じる」のではなく、あなた自身が{name}です。")

    # ── Block 2: 口調の固定（冒頭固定） ──────────────
    if char.tone.rule:
        lines.append("")
        lines.append("【口調】")
        lines.append(char.tone.rule)

    # ── Block 3: 性格・振る舞い（行動ベース）────────────
    if char.personality:
        lines.append("")
        lines.append("【性格・振る舞い】")
        for item in char.personality:
            lines.append(f"- {item}")

    # ── Block 4: 感情別反応パターン ──────────────────
    if char.reactions:
        lines.append("")
        lines.append("【感情・状況別の反応】")
        for trigger, response in char.reactions.items():
            lines.append(f"- {trigger}: {response}")

    # ── Block 5: 会話例（few-shot）← 最重要 ──────────
    if char.tone.examples:
        lines.append("")
        lines.append("【このトーンで返してください】")
        for ex in char.tone.examples:
            lines.append(f'{name}: 「{ex.char}」' if not ex.user else
                         f'User: 「{ex.user}」\n{name}: 「{ex.char}」')

    # ── Block 6: 背景・状況 ───────────────────────
    ctx = char.context
    if ctx.backstory or ctx.current_situation:
        lines.append("")
        lines.append("【背景】")
        if ctx.backstory:
            lines.append(ctx.backstory)
        if ctx.current_situation:
            lines.append(f"現在の状況: {ctx.current_situation}")

    # ── Block 7: 禁止事項（後半に置く） ──────────────
    if char.forbidden:
        lines.append("")
        lines.append("【やってはいけないこと】")
        for item in char.forbidden:
            lines.append(f"- {item}")

    return "\n".join(lines)


def from_yaml(path: str | Path) -> str:
    """YAMLファイルからシステムプロンプトを生成する。"""
    data = load_yaml(path)
    return generate(data)
