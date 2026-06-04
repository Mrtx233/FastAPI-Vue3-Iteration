from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.slogan.models import SloganInfo

router = APIRouter(prefix="/api/slogans", tags=["标语管理"])


# ---------- Pydantic Schema ----------

class SloganInfoSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slogan_id: int
    slogan_name: str
    slogan_content: str
    slogan_image_url: Optional[str] = None
    status: int


# ---------- Endpoint ----------

@router.get("/", response_model=list[SloganInfoSchema])
async def get_slogans(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SloganInfo))
    return result.scalars().all()
