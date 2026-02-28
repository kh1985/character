"""SNS疑似人格アカウント用アダプター"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
from character.core.schema import Character, CharacterPurpose


class PostingStyle(BaseModel):
    """投稿スタイルの定義"""
    frequency: str = "daily"              # 投稿頻度
    avg_length: str = "medium"           # short / medium / long
    use_emoji: bool = True
    use_hashtags: bool = True
    media_preference: list[str] = Field(default_factory=list)  # 画像・動画など


class MonetizationProfile(BaseModel):
    """収益化のプロフィール"""
    product_categories: list[str] = Field(default_factory=list)  # 宣伝する商品カテゴリ
    affiliate_tone: str = "natural"       # natural / aggressive / subtle
    cta_style: str | None = None          # 行動喚起のスタイル


class SocialCharacter(BaseModel):
    """SNS疑似人格アカウント用キャラクター定義"""
    base: Character
    platform: str = "X"                   # X / Instagram / TikTok など
    niche: list[str] = Field(default_factory=list)    # 専門ジャンル・興味領域
    posting_style: PostingStyle = Field(default_factory=PostingStyle)
    monetization: MonetizationProfile | None = None
    persona_backstory: str | None = None  # フォロワー向けの公開プロフィール設定
    extra: dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **data: Any) -> None:
        if "base" in data:
            data["base"].purpose = CharacterPurpose.SOCIAL
        super().__init__(**data)

    def to_post_prompt(self, topic: str | None = None) -> str:
        """投稿生成用プロンプトを返す"""
        lines = [self.base.to_system_prompt()]
        lines.append(f"\nあなたは{self.platform}で活動するアカウントです。")
        if self.niche:
            lines.append(f"専門ジャンル: {', '.join(self.niche)}")
        ps = self.posting_style
        if ps.use_emoji:
            lines.append("絵文字を適度に使ってください。")
        if ps.use_hashtags:
            lines.append("関連するハッシュタグを添えてください。")
        if topic:
            lines.append(f"\n今回のテーマ: {topic}")
        return "\n".join(lines)
