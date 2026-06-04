from typing import Optional

from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules import Base


class SloganInfo(Base):
    __tablename__ = "t_slogan_info"

    slogan_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="标语ID"
    )
    slogan_name: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="标语名称"
    )
    slogan_content: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="标语内容"
    )
    slogan_image_url: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="标语图片URL"
    )
    status: Mapped[int] = mapped_column(
        Integer, default=1, comment="状态"
    )
