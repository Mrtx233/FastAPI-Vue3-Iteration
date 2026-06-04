from datetime import date, datetime
from typing import Optional

from sqlalchemy import BigInteger, Date, DateTime, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules import Base


class ActivityEvent(Base):
    __tablename__ = "t_activity_event"

    event_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="赛事ID"
    )
    title: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="标题"
    )
    event_date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="赛事日期"
    )
    location: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="地点"
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="状态"
    )
    description: Mapped[str] = mapped_column(
        Text, nullable=False, comment="描述"
    )
    tags: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="标签"
    )
    prize: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="奖项"
    )
    scale: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="规模"
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="创建时间",
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
        comment="更新时间",
    )
