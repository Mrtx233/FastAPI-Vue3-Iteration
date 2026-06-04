from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from .models import StoreProvince, Store, UserStore

router = APIRouter(prefix="/api/stores", tags=["门店管理"])


# ---------- Pydantic Schemas ----------

class ProvinceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    province_id: int
    province_name: str
    center_lng: float | None = None
    center_lat: float | None = None


class StoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    store_id: int
    store_name: str
    store_type: int
    province_id: int
    province_name: str | None = None
    city: str | None = None
    district: str | None = None
    address: str | None = None
    store_phone: str | None = None
    store_image_url: str | None = None
    store_introduction: str | None = None
    business_hours: str | None = None
    is_operating: int
    store_lng: float | None = None
    store_lat: float | None = None


class UserStoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    role_id: int
    store_id: int
    created_at: datetime | None = None


# ---------- Endpoints ----------

@router.get("/provinces", response_model=list[ProvinceOut])
async def list_provinces(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StoreProvince))
    return result.scalars().all()


@router.get("/", response_model=list[StoreOut])
async def list_stores(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Store))
    return result.scalars().all()


@router.get("/user-stores", response_model=list[UserStoreOut])
async def list_user_stores(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserStore))
    return result.scalars().all()
