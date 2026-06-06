from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_permission
from app.core.database import get_db
from .models import CourseCategory, Course, UserCourseFavorite

router = APIRouter(prefix="/api/courses", tags=["课程管理"], dependencies=[Depends(require_permission('course:list'))])


# ---------- Pydantic Schemas ----------

class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: int
    category_name: str
    category_url: str | None = None
    description: str | None = None
    status: int


class CourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    course_id: int
    course_name: str
    category_id: int
    course_difficulty: int | None = None
    duration_minutes: int | None = None
    max_participants: int | None = None
    schedule_info: str | None = None
    description: str | None = None
    status: int


class UserCourseFavoriteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    favorite_id: int
    user_id: int
    course_id: int
    created_at: datetime | None = None


# ---------- Endpoints ----------

@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CourseCategory))
    return result.scalars().all()


@router.get("/", response_model=list[CourseOut])
async def list_courses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Course))
    return result.scalars().all()


@router.get("/category/{category_id}", response_model=list[CourseOut])
async def list_courses_by_category(category_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Course).where(Course.category_id == category_id))
    return result.scalars().all()


@router.get("/favorites/me", response_model=list[CourseOut])
async def list_my_favorite_courses(
    current_user: dict = Depends(require_permission('course:list')),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Course)
        .join(UserCourseFavorite, UserCourseFavorite.course_id == Course.course_id)
        .where(UserCourseFavorite.user_id == current_user["user_id"])
    )
    return result.scalars().all()


@router.get("/favorites", response_model=list[UserCourseFavoriteOut])
async def list_favorites(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserCourseFavorite))
    return result.scalars().all()
