"""
キャラクタープロンプトジェネレーター

YAMLで定義されたキャラクターを読み込み、
ブレにくいシステムプロンプトを業界標準の順序で生成する。

生成順序（重要度順）:
  1. アイデンティティ宣言
  2. 口調の固定（最重要）
  3. 禁止事項
  4. 性格（行動ベースの記述）
  5. 会話例 （few-shot）← 一番ブレを防ぐ
  6. 背景・状況
"""

from __future__ import annotations

from pathlib import Path
import yaml


def load_yaml(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def generate(data: dict) -> str:
    """
    キャラクター定義dictからシステムプロンプトを生成する。
    """
    lines: list[str] = []

    # ── Block 1: アイデンティティ宣言 ──────────────
    name = data["name"]
    age = data.get("age")
    occupation = data.get("occupation")

    age_str = f"{age}歳、" if age else ""
    occ_str = f"{occupation}の" if occupation else ""
    lines.append(f"あなたは{occ_str}{name}（{age_str}）です。{name}として返答してください。")
    lines.append(f"「演じる」のではなく、あなた自身が{name}です。")

    # ── Block 2: 口調の固定（冒頭固定がベスト） ──────
    tone = data.get("tone", {})
    if tone.get("rule"):
        lines.append("")
        lines.append("【口調】")
        lines.append(tone["rule"])

    # ── Block 3: 禁止事項 ────────────────────────
    forbidden = data.get("forbidden", [])
    if forbidden:
        lines.append("")
        lines.append("【禁止事項】")
        for item in forbidden:
            lines.append(f"- {item}")

    # ── Block 4: 性格（行動ベース）────────────────
    personality = data.get("personality", [])
    if personality:
        lines.append("")
        lines.append("【性格・振る舞い】")
        for item in personality:
            lines.append(f"- {item}")

    # ── Block 5: 会話例（few-shot）← 最重要 ─────────
    examples = tone.get("examples", [])
    if examples:
        lines.append("")
        lines.append("【このトーンで返してください】")
        for ex in examples:
            lines.append(f'User: 「{ex["user"]}」')
            lines.append(f'エマ: 「{ex["char"]}」')

    # ── Block 6: 背景・状況 ──────────────────────
    ctx = data.get("context", {})
    if ctx.get("backstory") or ctx.get("current_situation"):
        lines.append("")
        lines.append("【背景】")
        if ctx.get("backstory"):
            lines.append(ctx["backstory"])
        if ctx.get("current_situation"):
            lines.append(f"現在の状況: {ctx['current_situation']}")

    return "\n".join(lines)


def from_yaml(path: str | Path) -> str:
    """YAMLファイルからシステムプロンプトを生成する。"""
    data = load_yaml(path)
    return generate(data)
