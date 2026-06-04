from datetime import datetime

from sqlalchemy import BigInteger, Integer, String, Text, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modules import Base


class StoreProvince(Base):
    __tablename__ = "t_store_province"

    province_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="省份ID")
    province_name: Mapped[str] = mapped_column(String(64), nullable=False, comment="省份名称")
    center_lng: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True, comment="中心经度")
    center_lat: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True, comment="中心纬度")


class Store(Base):
    __tablename__ = "t_store"

    store_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="门店ID")
    store_name: Mapped[str] = mapped_column(String(64), nullable=False, comment="门店名称")
    store_type: Mapped[int] = mapped_column(Integer, nullable=False, comment="门店类型")
    province_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="省份ID")
    province_name: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="省份名称")
    city: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="城市")
    district: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="区县")
    address: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="详细地址")
    store_phone: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="门店电话")
    store_image_url: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="门店图片URL")
    store_introduction: Mapped[str | None] = mapped_column(Text, nullable=True, comment="门店介绍")
    business_hours: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="营业时间")
    is_operating: Mapped[int] = mapped_column(Integer, default=1, comment="是否营业")
    store_lng: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True, comment="门店经度")
    store_lat: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True, comment="门店纬度")


class UserStore(Base):
    __tablename__ = "y_user_store"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="用户ID")
    role_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="角色ID")
    store_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="门店ID")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), comment="创建时间")
