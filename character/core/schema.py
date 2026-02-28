"""
汎用キャラクター定義のコアスキーマ

どの用途（TRPG・SNS疑似人格・ギャルゲー・テストプレイヤー等）でも共通する
キャラクターの本質的な構造を定義する。
各用途固有の要素はアダプター側で拡張する。
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────
# 列挙型
# ─────────────────────────────────────────────

class CharacterPurpose(str, Enum):
    """キャラクターの用途"""
    TRPG = "trpg"
    SOCIAL = "social"        # SNS疑似人格
    GALGE = "galge"          # ギャルゲーヒロイン
    TESTER = "tester"        # テストプレイヤー
    GENERIC = "generic"      # 汎用


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NONBINARY = "nonbinary"
    UNSPECIFIED = "unspecified"


class ToneStyle(str, Enum):
    """口調のスタイル"""
    FORMAL = "formal"          # 丁寧語
    CASUAL = "casual"          # タメ口
    CHILDLIKE = "childlike"    # 子供っぽい
    COOL = "cool"              # クール・無口
    ENERGETIC = "energetic"    # 元気・テンション高め
    INTELLECTUAL = "intellectual"  # 知的・論理的
    CUTE = "cute"              # 甘え・かわいい系
    ROUGH = "rough"            # 荒っぽい・ぶっきらぼう


# ─────────────────────────────────────────────
# アイデンティティ層
# ─────────────────────────────────────────────

class Appearance(BaseModel):
    """外見の定義"""
    height_cm: int | None = None
    hair_color: str | None = None
    hair_style: str | None = None
    eye_color: str | None = None
    body_type: str | None = None
    notable_features: list[str] = Field(default_factory=list)
    visual_description: str | None = None  # 自由記述


class Identity(BaseModel):
    """アイデンティティ層：キャラクターの基本属性"""
    name: str
    age: int | None = None
    age_range: str | None = None   # 「10代後半」のような曖昧な表現用
    gender: Gender = Gender.UNSPECIFIED
    appearance: Appearance = Field(default_factory=Appearance)
    occupation: str | None = None
    nationality: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


# ─────────────────────────────────────────────
# パーソナリティ層
# ─────────────────────────────────────────────

class EmotionalTendency(BaseModel):
    """感情傾向"""
    baseline_mood: str = "neutral"       # 普段の感情状態
    anger_threshold: str = "medium"      # low / medium / high
    empathy_level: str = "medium"
    emotional_stability: str = "medium"


class Personality(BaseModel):
    """パーソナリティ層：性格・思考・感情パターン"""
    traits: list[str] = Field(
        default_factory=list,
        description="性格特性のリスト（例: ['明るい', '好奇心旺盛', '頑固']）"
    )
    values: list[str] = Field(
        default_factory=list,
        description="価値観・信念（例: ['家族を大切にする', '正直でいたい']）"
    )
    tone_style: ToneStyle = ToneStyle.CASUAL
    tone_description: str | None = None  # 口調の補足説明
    thinking_style: str | None = None   # 思考スタイルの説明
    emotional_tendency: EmotionalTendency = Field(default_factory=EmotionalTendency)
    mbti: str | None = None              # MBTI（任意）
    extra: dict[str, Any] = Field(default_factory=dict)


# ─────────────────────────────────────────────
# コンテキスト層
# ─────────────────────────────────────────────

class Relationship(BaseModel):
    """他キャラクターとの関係性"""
    target_name: str
    relation_type: str   # 「親友」「ライバル」「師匠」など
    description: str | None = None


class Context(BaseModel):
    """コンテキスト層：背景・経歴・目的"""
    backstory: str | None = None          # 生い立ち・背景ストーリー
    current_situation: str | None = None  # 現在の状況
    goals: list[str] = Field(default_factory=list)      # 目的・目標
    fears: list[str] = Field(default_factory=list)      # 恐れ・弱点
    secrets: list[str] = Field(default_factory=list)    # 秘密（非公開情報）
    relationships: list[Relationship] = Field(default_factory=list)
    world_setting: str | None = None      # 世界観・舞台設定
    extra: dict[str, Any] = Field(default_factory=dict)


# ─────────────────────────────────────────────
# 振る舞い層
# ─────────────────────────────────────────────

class ReactionPattern(BaseModel):
    """特定の状況に対する反応パターン"""
    trigger: str       # どんな状況で
    response: str      # どう反応するか
    example: str | None = None


class BehaviorPattern(BaseModel):
    """振る舞い層：行動・発話・反応のパターン"""
    catchphrases: list[str] = Field(default_factory=list)   # 口癖
    speech_patterns: list[str] = Field(default_factory=list) # 発話パターン（例: 語尾「だよ！」）
    reaction_patterns: list[ReactionPattern] = Field(default_factory=list)
    forbidden_topics: list[str] = Field(default_factory=list)  # 話したがらない話題
    favorite_topics: list[str] = Field(default_factory=list)   # よく話す話題
    system_prompt_notes: str | None = None  # LLMプロンプトへの追加指示
    extra: dict[str, Any] = Field(default_factory=dict)


# ─────────────────────────────────────────────
# コアキャラクター（統合）
# ─────────────────────────────────────────────

class Character(BaseModel):
    """
    汎用キャラクター定義

    全ての用途に共通するコアデータ。
    用途固有の拡張はアダプター（TRPGCharacter等）で行う。
    """
    purpose: CharacterPurpose = CharacterPurpose.GENERIC
    identity: Identity
    personality: Personality = Field(default_factory=Personality)
    context: Context = Field(default_factory=Context)
    behavior: BehaviorPattern = Field(default_factory=BehaviorPattern)

    def to_system_prompt(self) -> str:
        """
        LLMのシステムプロンプト用テキストを生成する。
        このキャラクターとして振る舞うための基本プロンプト。
        """
        lines: list[str] = []

        # アイデンティティ
        id_ = self.identity
        age_str = f"{id_.age}歳" if id_.age else id_.age_range or "年齢不明"
        lines.append(f"あなたは{id_.name}（{age_str}）として振る舞ってください。")
        if id_.occupation:
            lines.append(f"職業・立場: {id_.occupation}")

        # パーソナリティ
        p = self.personality
        if p.traits:
            lines.append(f"性格: {', '.join(p.traits)}")
        if p.values:
            lines.append(f"価値観: {', '.join(p.values)}")
        if p.tone_description:
            lines.append(f"口調: {p.tone_description}")
        elif p.tone_style != ToneStyle.CASUAL:
            lines.append(f"口調スタイル: {p.tone_style.value}")
        if p.thinking_style:
            lines.append(f"思考スタイル: {p.thinking_style}")

        # コンテキスト
        c = self.context
        if c.backstory:
            lines.append(f"\n【背景】\n{c.backstory}")
        if c.current_situation:
            lines.append(f"現在の状況: {c.current_situation}")
        if c.goals:
            lines.append(f"目標: {', '.join(c.goals)}")

        # 振る舞い
        b = self.behavior
        if b.catchphrases:
            lines.append(f"\n口癖: {', '.join(b.catchphrases)}")
        if b.speech_patterns:
            lines.append(f"話し方の特徴: {', '.join(b.speech_patterns)}")
        if b.forbidden_topics:
            lines.append(f"以下の話題は避けてください: {', '.join(b.forbidden_topics)}")
        if b.system_prompt_notes:
            lines.append(f"\n{b.system_prompt_notes}")

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)
