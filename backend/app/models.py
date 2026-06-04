from typing import Optional

from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SysUser(Base):
    __tablename__ = "sys_user"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="用户ID")
    username: Mapped[str] = mapped_column(String(64), nullable=False, comment="用户名")
    password: Mapped[str] = mapped_column(String(128), nullable=False, comment="密码")
    real_name: Mapped[Optional[str]] = mapped_column(String(64), default=None, comment="真实姓名")
    phone: Mapped[Optional[str]] = mapped_column(String(20), default=None, comment="手机号")
    status: Mapped[int] = mapped_column(Integer, default=1, comment="状态")
