"""TRPG用キャラクターアダプター"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
from character.core.schema import Character, CharacterPurpose


class Stat(BaseModel):
    """能力値"""
    name: str
    value: int
    max_value: int | None = None


class Skill(BaseModel):
    """スキル・特技"""
    name: str
    description: str | None = None
    level: int = 1


class TRPGCharacter(BaseModel):
    """TRPG用キャラクター定義"""
    base: Character
    character_class: str | None = None    # 職業クラス（戦士・魔法使いなど）
    race: str | None = None               # 種族
    alignment: str | None = None          # 陣営・属性（善・悪・中立など）
    level: int = 1
    stats: list[Stat] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    equipment: list[str] = Field(default_factory=list)
    extra: dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **data: Any) -> None:
        if "base" in data:
            data["base"].purpose = CharacterPurpose.TRPG
        super().__init__(**data)

    def to_system_prompt(self) -> str:
        lines = [self.base.to_system_prompt()]
        if self.character_class:
            lines.append(f"クラス: {self.character_class}")
        if self.race:
            lines.append(f"種族: {self.race}")
        if self.alignment:
            lines.append(f"属性: {self.alignment}")
        if self.skills:
            skill_names = [s.name for s in self.skills]
            lines.append(f"スキル: {', '.join(skill_names)}")
        return "\n".join(lines)
