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
  7. 禁止事項 ← 後半に置く（冒頭だとモデルが「防御的」になる）

参考:
  - Lost-in-the-Middle: 重要情報は冒頭か末尾に
  - 制約を冒頭に置くとキャラクター表現が硬直化する（コミュニティ実証）
  - Few-shot 3〜5例が最適（RoleLLM, ACL 2024）
  - 500〜700トークンがキャラクター用途の最適帯
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
    name = data["name"]
    age = data.get("age")
    occupation = data.get("occupation")

    # ── Block 1: アイデンティティ宣言 ──────────────
    age_str = f"{age}歳" if age else ""
    occ_str = f"{occupation}の" if occupation else ""
    age_occ = f"（{age_str}）" if age_str else ""
    lines.append(f"あなたは{occ_str}{name}{age_occ}です。{name}として返答してください。")
    lines.append(f"「演じる」のではなく、あなた自身が{name}です。")

    # ── Block 2: 口調の固定（冒頭固定） ──────────────
    tone = data.get("tone", {})
    if tone.get("rule"):
        lines.append("")
        lines.append("【口調】")
        lines.append(tone["rule"])

    # ── Block 3: 性格・振る舞い（行動ベース）────────────
    personality = data.get("personality", [])
    if personality:
        lines.append("")
        lines.append("【性格・振る舞い】")
        for item in personality:
            lines.append(f"- {item}")

    # ── Block 4: 感情別反応パターン ──────────────────
    reactions = data.get("reactions", {})
    if reactions:
        lines.append("")
        lines.append("【感情・状況別の反応】")
        for trigger, response in reactions.items():
            lines.append(f"- {trigger}のとき: {response}")

    # ── Block 5: 会話例（few-shot）← 最重要 ──────────
    examples = tone.get("examples", [])
    if examples:
        lines.append("")
        lines.append("【このトーンで返してください】")
        for ex in examples:
            lines.append(f'User: 「{ex["user"]}」')
            lines.append(f'{name}: 「{ex["char"]}」')

    # ── Block 6: 背景・状況 ───────────────────────
    ctx = data.get("context", {})
    if ctx.get("backstory") or ctx.get("current_situation"):
        lines.append("")
        lines.append("【背景】")
        if ctx.get("backstory"):
            lines.append(ctx["backstory"])
        if ctx.get("current_situation"):
            lines.append(f"現在の状況: {ctx['current_situation']}")

    # ── Block 7: 禁止事項（後半に置く） ──────────────
    forbidden = data.get("forbidden", [])
    if forbidden:
        lines.append("")
        lines.append("【やってはいけないこと】")
        for item in forbidden:
            lines.append(f"- {item}")

    return "\n".join(lines)


def from_yaml(path: str | Path) -> str:
    """YAMLファイルからシステムプロンプトを生成する。"""
    data = load_yaml(path)
    return generate(data)
