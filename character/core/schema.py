"""
キャラクター定義のスキーマ

実際のYAML構造に合わせたPydanticモデル。
generator.py・master.pyのバリデーションに使用する。
"""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class ToneExample(BaseModel):
    user: str
    char: str


class Tone(BaseModel):
    rule: str
    examples: list[ToneExample] = Field(default_factory=list)


class Context(BaseModel):
    backstory: str | None = None
    current_situation: str | None = None


class CharacterSheet(BaseModel):
    """
    キャラクター定義のフラットスキーマ。
    YAMLと1対1で対応する。
    """
    name: str
    age: int | None = None
    occupation: str | None = None
    tone: Tone = Field(default_factory=lambda: Tone(rule=""))
    personality: list[str] = Field(default_factory=list)
    reactions: dict[str, str] = Field(default_factory=dict)
    forbidden: list[str] = Field(default_factory=list)
    context: Context = Field(default_factory=Context)

    @model_validator(mode="after")
    def check_required_content(self) -> "CharacterSheet":
        if not self.tone.rule:
            raise ValueError(f"[{self.name}] tone.rule が空です")
        if not self.personality:
            raise ValueError(f"[{self.name}] personality が空です")
        return self

    @classmethod
    def from_dict(cls, data: dict) -> "CharacterSheet":
        return cls.model_validate(data)
