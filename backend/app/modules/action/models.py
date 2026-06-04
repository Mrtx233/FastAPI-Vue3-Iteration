from datetime import datetime

from sqlalchemy import BigInteger, Integer, String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modules import Base


class ActionCategory(Base):
    __tablename__ = "t_action_category"

    category_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="分类ID")
    category_name: Mapped[str] = mapped_column(String(64), nullable=False, comment="分类名称")
    category_image_url: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="分类图片URL")


class Action(Base):
    __tablename__ = "t_action"

    action_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="动作ID")
    action_name: Mapped[str] = mapped_column(String(64), nullable=False, comment="动作名称")
    category_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="分类ID")
    action_difficulty: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="动作难度")
    action_image_url: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="动作图片URL")
    action_steps: Mapped[str | None] = mapped_column(Text, nullable=True, comment="动作步骤")
    attention_points: Mapped[str | None] = mapped_column(Text, nullable=True, comment="注意事项")
    applicable_equipment: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="适用器材")
    applicable_store_type: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="适用门店类型")


class UserActionFavorite(Base):
    __tablename__ = "y_user_action_favorite"

    favorite_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="收藏ID")
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="用户ID")
    action_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="动作ID")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), comment="创建时间")
