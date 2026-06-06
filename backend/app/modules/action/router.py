from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_permission
from app.core.database import get_db
from .models import ActionCategory, Action, UserActionFavorite

router = APIRouter(prefix="/api/actions", tags=["动作库"], dependencies=[Depends(require_permission('action:list'))])


# ---------- Pydantic Schemas ----------

class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: int
    category_name: str
    category_image_url: str | None = None


class ActionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    action_id: int
    action_name: str
    category_id: int
    action_difficulty: int | None = None
    action_image_url: str | None = None
    action_steps: str | None = None
    attention_points: str | None = None
    applicable_equipment: str | None = None
    applicable_store_type: int | None = None


class UserActionFavoriteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    favorite_id: int
    user_id: int
    action_id: int
    created_at: datetime | None = None


# ---------- Endpoints ----------

@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ActionCategory))
    return result.scalars().all()


@router.get("/", response_model=list[ActionOut])
async def list_actions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Action))
    return result.scalars().all()


@router.get("/category/{category_id}", response_model=list[ActionOut])
async def list_actions_by_category(category_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Action).where(Action.category_id == category_id))
    return result.scalars().all()


@router.get("/favorites/me", response_model=list[ActionOut])
async def list_my_favorite_actions(
    current_user: dict = Depends(require_permission('action:list')),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Action)
        .join(UserActionFavorite, UserActionFavorite.action_id == Action.action_id)
        .where(UserActionFavorite.user_id == current_user["user_id"])
    )
    return result.scalars().all()


@router.get("/favorites", response_model=list[UserActionFavoriteOut])
async def list_favorites(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserActionFavorite))
    return result.scalars().all()
