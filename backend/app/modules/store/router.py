from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, require_permission
from app.core.database import get_db
from app.core.schemas import PaginatedResponse, paginated_query
from .models import StoreProvince, Store, UserStore

router = APIRouter(prefix="/api/stores", tags=["门店管理"])


# ---------- Pydantic Schemas ----------

class ProvinceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    province_id: int
    province_name: str
    center_lng: float | None = None
    center_lat: float | None = None


class ProvinceCreate(BaseModel):
    province_name: str
    center_lng: Optional[float] = None
    center_lat: Optional[float] = None


class ProvinceUpdate(BaseModel):
    province_name: Optional[str] = None
    center_lng: Optional[float] = None
    center_lat: Optional[float] = None


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


class StoreCreate(BaseModel):
    store_name: str
    store_type: int
    province_id: int
    province_name: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    store_phone: Optional[str] = None
    store_image_url: Optional[str] = None
    store_introduction: Optional[str] = None
    business_hours: Optional[str] = None
    is_operating: int = 1
    store_lng: Optional[float] = None
    store_lat: Optional[float] = None


class StoreUpdate(BaseModel):
    store_name: Optional[str] = None
    store_type: Optional[int] = None
    province_id: Optional[int] = None
    province_name: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    store_phone: Optional[str] = None
    store_image_url: Optional[str] = None
    store_introduction: Optional[str] = None
    business_hours: Optional[str] = None
    is_operating: Optional[int] = None
    store_lng: Optional[float] = None
    store_lat: Optional[float] = None


class UserStoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    role_id: int
    store_id: int
    created_at: datetime | None = None


# ==================== 省份区域 ====================

@router.get("/provinces", response_model=list[ProvinceOut],
            dependencies=[Depends(require_permission('store:list'))])
async def list_provinces(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StoreProvince))
    return result.scalars().all()


@router.get("/provinces/{province_id}", response_model=ProvinceOut,
            dependencies=[Depends(require_permission('store:list'))])
async def get_province(province_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StoreProvince).where(StoreProvince.province_id == province_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "省份不存在")
    return obj


@router.post("/provinces", response_model=ProvinceOut,
             dependencies=[Depends(require_permission('province:create'))])
async def create_province(data: ProvinceCreate, db: AsyncSession = Depends(get_db)):
    obj = StoreProvince(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.put("/provinces/{province_id}", response_model=ProvinceOut,
            dependencies=[Depends(require_permission('province:edit'))])
async def update_province(province_id: int, data: ProvinceUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StoreProvince).where(StoreProvince.province_id == province_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "省份不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/provinces/{province_id}",
               dependencies=[Depends(require_permission('province:delete'))])
async def delete_province(province_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StoreProvince).where(StoreProvince.province_id == province_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "省份不存在")
    await db.delete(obj)
    await db.commit()
    return {"detail": "删除成功"}


# ==================== 门店信息 ====================

@router.get("/",
            dependencies=[Depends(require_permission('store:list'))])
async def list_stores(
    page: int = 1,
    page_size: int = 20,
    keyword: str | None = None,
    is_operating: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await paginated_query(
        db, Store,
        page=page, page_size=page_size,
        keyword=keyword,
        keyword_fields=[Store.store_name, Store.city],
        status_field=Store.is_operating, status_value=is_operating,
    )


@router.post("/", response_model=StoreOut,
             dependencies=[Depends(require_permission('store:create'))])
async def create_store(data: StoreCreate, db: AsyncSession = Depends(get_db)):
    obj = Store(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.put("/{store_id}", response_model=StoreOut,
            dependencies=[Depends(require_permission('store:edit'))])
async def update_store(store_id: int, data: StoreUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Store).where(Store.store_id == store_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "门店不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/{store_id}",
               dependencies=[Depends(require_permission('store:delete'))])
async def delete_store(store_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Store).where(Store.store_id == store_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "门店不存在")
    await db.delete(obj)
    await db.commit()
    return {"detail": "删除成功"}


# ==================== 用户门店关联 ====================

class UserStoreCreate(BaseModel):
    user_id: int
    role_id: int
    store_id: int


class UserStoreUpdate(BaseModel):
    user_id: Optional[int] = None
    role_id: Optional[int] = None
    store_id: Optional[int] = None


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


@router.get("/user-stores/{us_id}", response_model=UserStoreOut,
            dependencies=[Depends(require_permission('store:list'))])
async def get_user_store(us_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserStore).where(UserStore.id == us_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "用户门店关联不存在")
    return obj


@router.post("/user-stores", response_model=UserStoreOut,
             dependencies=[Depends(require_permission('user_store:create'))])
async def create_user_store(data: UserStoreCreate, db: AsyncSession = Depends(get_db)):
    # 检查是否已存在相同关联
    existing = await db.execute(
        select(UserStore).where(
            UserStore.user_id == data.user_id,
            UserStore.store_id == data.store_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, "该用户已关联此门店")
    obj = UserStore(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.put("/user-stores/{us_id}", response_model=UserStoreOut,
            dependencies=[Depends(require_permission('user_store:edit'))])
async def update_user_store(us_id: int, data: UserStoreUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserStore).where(UserStore.id == us_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "用户门店关联不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/user-stores/{us_id}",
               dependencies=[Depends(require_permission('user_store:delete'))])
async def delete_user_store(us_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserStore).where(UserStore.id == us_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "用户门店关联不存在")
    await db.delete(obj)
    await db.commit()
    return {"detail": "删除成功"}


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
