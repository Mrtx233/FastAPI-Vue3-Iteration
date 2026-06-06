from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, require_permission
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

@router.get("/provinces", response_model=list[ProvinceOut],
            dependencies=[Depends(require_permission('store:list'))])
async def list_provinces(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StoreProvince))
    return result.scalars().all()


@router.get("/", response_model=list[StoreOut],
            dependencies=[Depends(require_permission('store:list'))])
async def list_stores(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Store))
    return result.scalars().all()


@router.get("/user-stores", response_model=list[UserStoreOut],
            dependencies=[Depends(require_permission('store:list'))])
async def list_user_stores(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserStore))
    return result.scalars().all()


@router.get("/user-stores/by-user/{user_id}", response_model=list[UserStoreOut])
async def list_user_stores_by_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user["role_id"] not in (1, 2) and current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能查询自己的门店关联",
        )

    result = await db.execute(select(UserStore).where(UserStore.user_id == user_id))
    return result.scalars().all()


@router.get("/{store_id}", response_model=StoreOut)
async def get_store_by_id(
    store_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user["role_id"] not in (1, 2):
        user_store_result = await db.execute(
            select(UserStore).where(
                UserStore.user_id == current_user["user_id"],
                UserStore.store_id == store_id,
            )
        )
        if user_store_result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能查询自己关联的门店",
            )

    result = await db.execute(select(Store).where(Store.store_id == store_id))
    store = result.scalar_one_or_none()
    if store is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="门店不存在")
    return store
