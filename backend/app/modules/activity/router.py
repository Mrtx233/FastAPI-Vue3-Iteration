from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_permission
from app.core.database import get_db
from app.modules.activity.models import ActivityEvent

router = APIRouter(prefix="/api/activities", tags=["赛事活动"],
                   dependencies=[Depends(require_permission('activity:list'))])


# ---------- Pydantic Schemas ----------

class ActivityEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: int
    title: str
    event_date: date
    location: str
    status: str
    description: str
    tags: Optional[str] = None
    prize: Optional[str] = None
    scale: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ActivityCreate(BaseModel):
    title: str
    event_date: date
    location: str
    status: str
    description: str
    tags: Optional[str] = None
    prize: Optional[str] = None
    scale: Optional[str] = None


class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    event_date: Optional[date] = None
    location: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    prize: Optional[str] = None
    scale: Optional[str] = None


# ---------- Endpoints ----------

@router.get("/", response_model=list[ActivityEventSchema])
async def get_activities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ActivityEvent))
    return result.scalars().all()


@router.get("/{event_id}", response_model=ActivityEventSchema)
async def get_activity(event_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ActivityEvent).where(ActivityEvent.event_id == event_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "活动不存在")
    return obj


@router.post("/", response_model=ActivityEventSchema,
             dependencies=[Depends(require_permission('activity:create'))])
async def create_activity(data: ActivityCreate, db: AsyncSession = Depends(get_db)):
    obj = ActivityEvent(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.put("/{event_id}", response_model=ActivityEventSchema,
            dependencies=[Depends(require_permission('activity:edit'))])
async def update_activity(event_id: int, data: ActivityUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ActivityEvent).where(ActivityEvent.event_id == event_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "活动不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/{event_id}",
               dependencies=[Depends(require_permission('activity:delete'))])
async def delete_activity(event_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ActivityEvent).where(ActivityEvent.event_id == event_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "活动不存在")
    await db.delete(obj)
    await db.commit()
    return {"detail": "删除成功"}
