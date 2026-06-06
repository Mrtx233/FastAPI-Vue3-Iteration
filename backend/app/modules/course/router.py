from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, require_permission
from app.core.database import get_db
from app.core.schemas import PaginatedResponse, paginated_query
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


class CourseCategoryCreate(BaseModel):
    category_name: str
    category_url: str | None = None
    description: str | None = None
    status: int = 1


class CourseCategoryUpdate(BaseModel):
    category_name: str | None = None
    category_url: str | None = None
    description: str | None = None
    status: int | None = None


class CourseCreate(BaseModel):
    course_name: str
    category_id: int
    course_difficulty: int | None = None
    duration_minutes: int | None = None
    max_participants: int | None = None
    schedule_info: str | None = None
    description: str | None = None
    status: int = 1


class CourseUpdate(BaseModel):
    course_name: str | None = None
    category_id: int | None = None
    course_difficulty: int | None = None
    duration_minutes: int | None = None
    max_participants: int | None = None
    schedule_info: str | None = None
    description: str | None = None
    status: int | None = None


class UserCourseFavoriteCreate(BaseModel):
    course_id: int


class UserCourseFavoriteUpdate(BaseModel):
    course_id: int | None = None


# ---------- Endpoints ----------

# --- 课程分类 CRUD ---

@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CourseCategory))
    return result.scalars().all()


@router.get("/categories/{category_id}", response_model=CategoryOut)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CourseCategory).where(CourseCategory.category_id == category_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "课程分类不存在")
    return obj


@router.post("/categories", response_model=CategoryOut,
             dependencies=[Depends(require_permission('course_category:create'))])
async def create_category(data: CourseCategoryCreate, db: AsyncSession = Depends(get_db)):
    obj = CourseCategory(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.put("/categories/{category_id}", response_model=CategoryOut,
            dependencies=[Depends(require_permission('course_category:edit'))])
async def update_category(category_id: int, data: CourseCategoryUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CourseCategory).where(CourseCategory.category_id == category_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "课程分类不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/categories/{category_id}",
               dependencies=[Depends(require_permission('course_category:delete'))])
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CourseCategory).where(CourseCategory.category_id == category_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "课程分类不存在")
    await db.delete(obj)
    await db.commit()
    return {"detail": "删除成功"}


# --- 课程 CRUD ---

@router.get("/")
async def list_courses(
    page: int = 1,
    page_size: int = 20,
    keyword: str | None = None,
    status: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await paginated_query(
        db, Course,
        page=page, page_size=page_size,
        keyword=keyword,
        keyword_fields=[Course.course_name],
        status_field=Course.status, status_value=status,
    )


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


@router.get("/favorites/{favorite_id}", response_model=UserCourseFavoriteOut)
async def get_favorite(
    favorite_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserCourseFavorite).where(UserCourseFavorite.favorite_id == favorite_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "收藏记录不存在")
    # 非管理员只能查看自己的收藏
    if current_user["role_id"] not in (1, 2) and obj.user_id != current_user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能查看自己的收藏")
    return obj


@router.post("/favorites", response_model=UserCourseFavoriteOut,
             dependencies=[Depends(require_permission('course_favorite:create'))])
async def create_favorite(
    data: UserCourseFavoriteCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 检查是否已收藏
    existing = await db.execute(
        select(UserCourseFavorite).where(
            UserCourseFavorite.user_id == current_user["user_id"],
            UserCourseFavorite.course_id == data.course_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, "已收藏该课程")
    obj = UserCourseFavorite(user_id=current_user["user_id"], course_id=data.course_id)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.put("/favorites/{favorite_id}", response_model=UserCourseFavoriteOut,
            dependencies=[Depends(require_permission('course_favorite:edit'))])
async def update_favorite(
    favorite_id: int,
    data: UserCourseFavoriteUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserCourseFavorite).where(UserCourseFavorite.favorite_id == favorite_id)
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
               dependencies=[Depends(require_permission('course_favorite:delete'))])
async def delete_favorite(
    favorite_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserCourseFavorite).where(UserCourseFavorite.favorite_id == favorite_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "收藏记录不存在")
    # 非管理员只能删除自己的收藏
    if current_user["role_id"] not in (1, 2) and obj.user_id != current_user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能删除自己的收藏")
    await db.delete(obj)
    await db.commit()
    return {"detail": "删除成功"}


# --- 课程 CRUD（放在最后，避免 /{course_id} 拦截 /categories/ 等路径） ---

@router.get("/{course_id}", response_model=CourseOut)
async def get_course(course_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Course).where(Course.course_id == course_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "课程不存在")
    return obj


@router.post("/", response_model=CourseOut,
             dependencies=[Depends(require_permission('course:create'))])
async def create_course(data: CourseCreate, db: AsyncSession = Depends(get_db)):
    obj = Course(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.put("/{course_id}", response_model=CourseOut,
            dependencies=[Depends(require_permission('course:edit'))])
async def update_course(course_id: int, data: CourseUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Course).where(Course.course_id == course_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "课程不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/{course_id}",
               dependencies=[Depends(require_permission('course:delete'))])
async def delete_course(course_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Course).where(Course.course_id == course_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "课程不存在")
    await db.delete(obj)
    await db.commit()
    return {"detail": "删除成功"}
