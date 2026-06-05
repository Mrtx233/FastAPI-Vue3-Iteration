from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_permission
from app.core.database import get_db
from app.modules.slogan.models import SloganInfo

router = APIRouter(prefix="/api/slogans", tags=["标语管理"])


# ---------- Pydantic Schemas ----------

class SloganInfoSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slogan_id: int
    slogan_name: str
    slogan_content: str
    slogan_image_url: Optional[str] = None
    status: int


class SloganCreate(BaseModel):
    slogan_name: str
    slogan_content: str
    slogan_image_url: Optional[str] = None
    status: int = 1


class SloganUpdate(BaseModel):
    slogan_name: Optional[str] = None
    slogan_content: Optional[str] = None
    slogan_image_url: Optional[str] = None
    status: Optional[int] = None


# ---------- Endpoints ----------

@router.get("/", response_model=list[SloganInfoSchema],
            dependencies=[Depends(require_permission('slogan:list'))])
async def get_slogans(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SloganInfo))
    return result.scalars().all()


@router.get("/{slogan_id}", response_model=SloganInfoSchema,
            dependencies=[Depends(require_permission('slogan:list'))])
async def get_slogan(slogan_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SloganInfo).where(SloganInfo.slogan_id == slogan_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "标语不存在")
    return obj


@router.post("/", response_model=SloganInfoSchema,
             dependencies=[Depends(require_permission('slogan:manage'))])
async def create_slogan(data: SloganCreate, db: AsyncSession = Depends(get_db)):
    obj = SloganInfo(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.put("/{slogan_id}", response_model=SloganInfoSchema,
            dependencies=[Depends(require_permission('slogan:manage'))])
async def update_slogan(slogan_id: int, data: SloganUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SloganInfo).where(SloganInfo.slogan_id == slogan_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "标语不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/{slogan_id}",
               dependencies=[Depends(require_permission('slogan:manage'))])
async def delete_slogan(slogan_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SloganInfo).where(SloganInfo.slogan_id == slogan_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "标语不存在")
    await db.delete(obj)
    await db.commit()
    return {"detail": "删除成功"}
