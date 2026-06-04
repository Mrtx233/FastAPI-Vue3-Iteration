from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.activity.models import ActivityEvent

router = APIRouter(prefix="/api/activities", tags=["赛事活动"])


# ---------- Pydantic Schema ----------

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


# ---------- Endpoint ----------

@router.get("/", response_model=list[ActivityEventSchema])
async def get_activities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ActivityEvent))
    return result.scalars().all()
