from datetime import datetime

from sqlalchemy import BigInteger, Integer, String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modules import Base


class CourseCategory(Base):
    __tablename__ = "t_course_category"

    category_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="分类ID")
    category_name: Mapped[str] = mapped_column(String(64), nullable=False, comment="分类名称")
    category_url: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="分类URL")
    description: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="描述")
    status: Mapped[int] = mapped_column(Integer, default=1, comment="状态")


class Course(Base):
    __tablename__ = "t_course"

    course_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="课程ID")
    course_name: Mapped[str] = mapped_column(String(64), nullable=False, comment="课程名称")
    category_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="分类ID")
    course_difficulty: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="课程难度")
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="时长(分钟)")
    max_participants: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="最大参与人数")
    schedule_info: Mapped[str | None] = mapped_column(Text, nullable=True, comment="排课信息")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="课程描述")
    status: Mapped[int] = mapped_column(Integer, default=1, comment="状态")


class UserCourseFavorite(Base):
    __tablename__ = "y_user_course_favorite"

    favorite_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="收藏ID")
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="用户ID")
    course_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="课程ID")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), comment="创建时间")
