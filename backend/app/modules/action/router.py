from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, require_permission
from app.core.database import get_db
from app.core.schemas import PaginatedResponse, paginated_query
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


class ActionCategoryCreate(BaseModel):
    category_name: str
    category_image_url: str | None = None


class ActionCategoryUpdate(BaseModel):
    category_name: str | None = None
    category_image_url: str | None = None


class ActionCreate(BaseModel):
    action_name: str
    category_id: int
    action_difficulty: int | None = None
    action_image_url: str | None = None
    action_steps: str | None = None
    attention_points: str | None = None
    applicable_equipment: str | None = None
    applicable_store_type: int | None = None


class ActionUpdate(BaseModel):
    action_name: str | None = None
    category_id: int | None = None
    action_difficulty: int | None = None
    action_image_url: str | None = None
    action_steps: str | None = None
    attention_points: str | None = None
    applicable_equipment: str | None = None
    applicable_store_type: int | None = None


class UserActionFavoriteCreate(BaseModel):
    action_id: int


class UserActionFavoriteUpdate(BaseModel):
    action_id: int | None = None


# ---------- Endpoints ----------

# --- 动作分类 CRUD ---

@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ActionCategory))
    return result.scalars().all()


@router.get("/categories/{category_id}", response_model=CategoryOut)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ActionCategory).where(ActionCategory.category_id == category_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "动作分类不存在")
    return obj


@router.post("/categories", response_model=CategoryOut,
             dependencies=[Depends(require_permission('action_category:create'))])
async def create_category(data: ActionCategoryCreate, db: AsyncSession = Depends(get_db)):
    obj = ActionCategory(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.put("/categories/{category_id}", response_model=CategoryOut,
            dependencies=[Depends(require_permission('action_category:edit'))])
async def update_category(category_id: int, data: ActionCategoryUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ActionCategory).where(ActionCategory.category_id == category_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "动作分类不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/categories/{category_id}",
               dependencies=[Depends(require_permission('action_category:delete'))])
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ActionCategory).where(ActionCategory.category_id == category_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "动作分类不存在")
    await db.delete(obj)
    await db.commit()
    return {"detail": "删除成功"}


# --- 动作 CRUD ---

@router.get("/")
async def list_actions(
    page: int = 1,
    page_size: int = 20,
    keyword: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await paginated_query(
        db, Action,
        page=page, page_size=page_size,
        keyword=keyword,
        keyword_fields=[Action.action_name],
    )


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


@router.get("/favorites/{favorite_id}", response_model=UserActionFavoriteOut)
async def get_favorite(
    favorite_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserActionFavorite).where(UserActionFavorite.favorite_id == favorite_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "收藏记录不存在")
    if current_user["role_id"] not in (1, 2) and obj.user_id != current_user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能查看自己的收藏")
    return obj


@router.post("/favorites", response_model=UserActionFavoriteOut,
             dependencies=[Depends(require_permission('action_favorite:create'))])
async def create_favorite(
    data: UserActionFavoriteCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(UserActionFavorite).where(
            UserActionFavorite.user_id == current_user["user_id"],
            UserActionFavorite.action_id == data.action_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, "已收藏该动作")
    obj = UserActionFavorite(user_id=current_user["user_id"], action_id=data.action_id)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.put("/favorites/{favorite_id}", response_model=UserActionFavoriteOut,
            dependencies=[Depends(require_permission('action_favorite:edit'))])
async def update_favorite(
    favorite_id: int,
    data: UserActionFavoriteUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserActionFavorite).where(UserActionFavorite.favorite_id == favorite_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "收藏记录不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/favorites/{favorite_id}",
               dependencies=[Depends(require_permission('action_favorite:delete'))])
async def delete_favorite(
    favorite_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserActionFavorite).where(UserActionFavorite.favorite_id == favorite_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "收藏记录不存在")
    if current_user["role_id"] not in (1, 2) and obj.user_id != current_user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能删除自己的收藏")
    await db.delete(obj)
    await db.commit()
    return {"detail": "删除成功"}


# --- 动作 CRUD（放在最后，避免 /{action_id} 拦截 /categories/ 等路径） ---

@router.get("/{action_id}", response_model=ActionOut)
async def get_action(action_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Action).where(Action.action_id == action_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "动作不存在")
    return obj


@router.post("/", response_model=ActionOut,
             dependencies=[Depends(require_permission('action:create'))])
async def create_action(data: ActionCreate, db: AsyncSession = Depends(get_db)):
    obj = Action(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.put("/{action_id}", response_model=ActionOut,
            dependencies=[Depends(require_permission('action:edit'))])
async def update_action(action_id: int, data: ActionUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Action).where(Action.action_id == action_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "动作不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/{action_id}",
               dependencies=[Depends(require_permission('action:delete'))])
async def delete_action(action_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Action).where(Action.action_id == action_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "动作不存在")
    await db.delete(obj)
    await db.commit()
    return {"detail": "删除成功"}
