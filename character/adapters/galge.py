"""ギャルゲーヒロイン用アダプター"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
from character.core.schema import Character, CharacterPurpose


class AffectionLevel(BaseModel):
    """好感度レベルの定義"""
    level: int = 0                 # 現在の好感度（0〜100）
    thresholds: dict[int, str] = Field(
        default_factory=lambda: {
            0: "他人",
            20: "知人",
            40: "友人",
            60: "親友",
            80: "特別",
            100: "攻略完了",
        }
    )

    @property
    def current_stage(self) -> str:
        for threshold in sorted(self.thresholds.keys(), reverse=True):
            if self.level >= threshold:
                return self.thresholds[threshold]
        return "他人"


class RouteFlag(BaseModel):
    """攻略ルートのフラグ"""
    flag_name: str
    description: str
    is_triggered: bool = False


class GalgeCharacter(BaseModel):
    """ギャルゲーヒロイン用キャラクター定義"""
    base: Character
    archetype: str | None = None           # ヒロイン類型（幼馴染・委員長・ツンデレなど）
    affection: AffectionLevel = Field(default_factory=AffectionLevel)
    route_flags: list[RouteFlag] = Field(default_factory=list)
    event_scenes: list[str] = Field(default_factory=list)     # イベント名のリスト
    voice_tone: str | None = None          # 声のイメージ
    theme_color: str | None = None         # イメージカラー
    extra: dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **data: Any) -> None:
        if "base" in data:
            data["base"].purpose = CharacterPurpose.GALGE
        super().__init__(**data)

    def to_system_prompt(self) -> str:
        lines = [self.base.to_system_prompt()]
        if self.archetype:
            lines.append(f"ヒロイン類型: {self.archetype}")
        stage = self.affection.current_stage
        lines.append(f"現在の関係性: {stage}（好感度{self.affection.level}）")
        return "\n".join(lines)
