from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Date, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules import Base


class SysPermission(Base):
    __tablename__ = "sys_permission"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="权限ID"
    )
    permission_code: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="权限编码"
    )
    permission_name: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="权限名称"
    )
    menu_path: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="菜单路径"
    )


class SysRole(Base):
    __tablename__ = "sys_role"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="角色ID"
    )
    role_code: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="角色编码"
    )
    role_name: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="角色名称"
    )


class SysRolePermission(Base):
    __tablename__ = "sys_role_permission"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="关联ID"
    )
    role_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="角色ID"
    )
    permission_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="权限ID"
    )


class SysUser(Base):
    __tablename__ = "sys_user"

    user_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="用户ID"
    )
    role_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="角色ID"
    )
    username: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="用户名"
    )
    password: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="密码"
    )
    real_name: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="真实姓名"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="手机号"
    )
    status: Mapped[int] = mapped_column(
        Integer, default=1, comment="状态"
    )


class SysUserProfile(Base):
    __tablename__ = "sys_user_profile"

    profile_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="档案ID"
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="用户ID"
    )
    level: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="等级"
    )
    gender: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="性别"
    )
    birthday: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="生日"
    )
    height_cm: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True, comment="身高(cm)"
    )
    weight_kg: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True, comment="体重(kg)"
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="头像URL"
    )
    intro: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="个人简介"
    )
    create_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="创建时间"
    )
    join_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="加入时间"
    )
    expire_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="到期日期"
    )
