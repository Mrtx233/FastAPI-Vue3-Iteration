from typing import Optional
from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import (
    verify_password, create_access_token, get_current_user,
    require_permission, hash_password,
)
from app.core.database import get_db
from app.core.schemas import PaginatedResponse, paginated_query
from app.modules.system.models import (
    SysPermission,
    SysRole,
    SysRolePermission,
    SysUser,
    SysUserProfile,
)

router = APIRouter(prefix="/api/system", tags=["系统管理"])


# ---------- Pydantic Schemas ----------

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role_id: int
    username: str


class CurrentUserResponse(BaseModel):
    user_id: int
    role_id: int
    username: str


# -- Permission --
class SysPermissionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    permission_code: str
    permission_name: str
    menu_path: Optional[str] = None


class SysPermissionCreate(BaseModel):
    permission_code: str
    permission_name: str
    menu_path: Optional[str] = None


class SysPermissionUpdate(BaseModel):
    permission_code: Optional[str] = None
    permission_name: Optional[str] = None
    menu_path: Optional[str] = None


# -- Role --
class SysRoleSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role_code: str
    role_name: str


class SysRoleCreate(BaseModel):
    role_code: str
    role_name: str


class SysRoleUpdate(BaseModel):
    role_code: Optional[str] = None
    role_name: Optional[str] = None


# -- Role Permission --
class SysRolePermissionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role_id: int
    permission_id: int


class SysRolePermissionCreate(BaseModel):
    role_id: int
    permission_id: int


# -- User --
class SysUserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    role_id: int
    username: str
    password: str
    real_name: Optional[str] = None
    phone: Optional[str] = None
    status: int


class SysUserCreate(BaseModel):
    role_id: int
    username: str
    password: str
    real_name: Optional[str] = None
    phone: Optional[str] = None
    status: int = 1


class SysUserUpdate(BaseModel):
    role_id: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    real_name: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[int] = None


# -- User Profile --
class SysUserProfileSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    profile_id: int
    user_id: int
    level: Optional[int] = None
    gender: Optional[int] = None
    birthday: Optional[date] = None
    height_cm: Optional[Decimal] = None
    weight_kg: Optional[Decimal] = None
    avatar_url: Optional[str] = None
    intro: Optional[str] = None
    create_time: Optional[datetime] = None
    join_time: Optional[datetime] = None
    expire_date: Optional[datetime] = None


class SysUserProfileCreate(BaseModel):
    user_id: int
    level: Optional[int] = None
    gender: Optional[int] = None
    birthday: Optional[date] = None
    height_cm: Optional[Decimal] = None
    weight_kg: Optional[Decimal] = None
    avatar_url: Optional[str] = None
    intro: Optional[str] = None
    create_time: Optional[datetime] = None
    join_time: Optional[datetime] = None
    expire_date: Optional[datetime] = None


class SysUserProfileUpdate(BaseModel):
    level: Optional[int] = None
    gender: Optional[int] = None
    birthday: Optional[date] = None
    height_cm: Optional[Decimal] = None
    weight_kg: Optional[Decimal] = None
    avatar_url: Optional[str] = None
    intro: Optional[str] = None
    create_time: Optional[datetime] = None
    join_time: Optional[datetime] = None
    expire_date: Optional[datetime] = None


# ==================== 登录 & 当前用户（无需鉴权） ====================

@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录，返回 JWT Token"""
    result = await db.execute(select(SysUser).where(SysUser.username == req.username))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(req.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    if user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用",
        )
    token = create_access_token(user.user_id, user.role_id, user.username)
    return LoginResponse(
        access_token=token,
        user_id=user.user_id,
        role_id=user.role_id,
        username=user.username,
    )


@router.get("/me", response_model=CurrentUserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return current_user


# ==================== 权限定义 CRUD ====================

@router.get("/permissions", response_model=list[SysPermissionSchema],
            dependencies=[Depends(require_permission('permission:list'))])
async def get_permissions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysPermission))
    return result.scalars().all()


@router.get("/permissions/{perm_id}", response_model=SysPermissionSchema,
            dependencies=[Depends(require_permission('permission:list'))])
async def get_permission(perm_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysPermission).where(SysPermission.id == perm_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "权限不存在")
    return obj


@router.post("/permissions", response_model=SysPermissionSchema,
             dependencies=[Depends(require_permission('permission:create'))])
async def create_permission(data: SysPermissionCreate, db: AsyncSession = Depends(get_db)):
    obj = SysPermission(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.put("/permissions/{perm_id}", response_model=SysPermissionSchema,
            dependencies=[Depends(require_permission('permission:edit'))])
async def update_permission(perm_id: int, data: SysPermissionUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysPermission).where(SysPermission.id == perm_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "权限不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/permissions/{perm_id}",
               dependencies=[Depends(require_permission('permission:delete'))])
async def delete_permission(perm_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysPermission).where(SysPermission.id == perm_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "权限不存在")
    await db.delete(obj)
    await db.commit()
    return {"detail": "删除成功"}


# ==================== 角色 CRUD ====================

@router.get("/roles", response_model=list[SysRoleSchema],
            dependencies=[Depends(require_permission('role:list'))])
async def get_roles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysRole))
    return result.scalars().all()


@router.get("/roles/{role_id}", response_model=SysRoleSchema,
            dependencies=[Depends(require_permission('role:list'))])
async def get_role(role_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysRole).where(SysRole.id == role_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "角色不存在")
    return obj


@router.post("/roles", response_model=SysRoleSchema,
             dependencies=[Depends(require_permission('role:create'))])
async def create_role(data: SysRoleCreate, db: AsyncSession = Depends(get_db)):
    obj = SysRole(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.put("/roles/{role_id}", response_model=SysRoleSchema,
            dependencies=[Depends(require_permission('role:edit'))])
async def update_role(role_id: int, data: SysRoleUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysRole).where(SysRole.id == role_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "角色不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/roles/{role_id}",
               dependencies=[Depends(require_permission('role:delete'))])
async def delete_role(role_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysRole).where(SysRole.id == role_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "角色不存在")
    # 同时删除该角色的权限关联
    await db.execute(delete(SysRolePermission).where(SysRolePermission.role_id == role_id))
    await db.delete(obj)
    await db.commit()
    return {"detail": "删除成功"}


# ==================== 角色权限关联 CRUD ====================

@router.get("/role-permissions", response_model=list[SysRolePermissionSchema],
            dependencies=[Depends(require_permission('role_permission:list'))])
async def get_role_permissions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysRolePermission))
    return result.scalars().all()


@router.post("/role-permissions", response_model=SysRolePermissionSchema,
             dependencies=[Depends(require_permission('role_permission:create'))])
async def create_role_permission(data: SysRolePermissionCreate, db: AsyncSession = Depends(get_db)):
    # 检查是否已存在
    result = await db.execute(
        select(SysRolePermission).where(
            SysRolePermission.role_id == data.role_id,
            SysRolePermission.permission_id == data.permission_id,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(400, "该角色已拥有此权限")
    obj = SysRolePermission(role_id=data.role_id, permission_id=data.permission_id)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/role-permissions/{rp_id}",
               dependencies=[Depends(require_permission('role_permission:delete'))])
async def delete_role_permission(rp_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysRolePermission).where(SysRolePermission.id == rp_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "角色权限关联不存在")
    await db.delete(obj)
    await db.commit()
    return {"detail": "删除成功"}


# ==================== 用户 CRUD ====================

def _require_user_view():
    """
    查看用户详情的权限依赖：
    - 拥有 user:list 可查看所有用户
    - 拥有 user:view_own 只能查看自己（在端点中二次校验）
    """
    async def checker(
        current_user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        from app.modules.system.models import SysRolePermission, SysPermission
        result = await db.execute(
            select(SysPermission.permission_code)
            .join(SysRolePermission, SysRolePermission.permission_id == SysPermission.id)
            .where(SysRolePermission.role_id == current_user["role_id"])
        )
        codes = set(row[0] for row in result.all())
        if "user:list" in codes:
            return current_user
        if "user:view_own" in codes:
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要: user:list 或 user:view_own",
        )
    return checker


@router.get("/users",
            dependencies=[Depends(require_permission('user:list'))])
async def get_users(
    page: int = 1,
    page_size: int = 20,
    keyword: str | None = None,
    status: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await paginated_query(
        db, SysUser,
        page=page, page_size=page_size,
        keyword=keyword,
        keyword_fields=[SysUser.username, SysUser.real_name],
        status_field=SysUser.status, status_value=status,
    )


@router.get("/users/{user_id}", response_model=SysUserSchema,
            dependencies=[Depends(_require_user_view())])
async def get_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # user:view_own 只能查看自己
    from app.modules.system.models import SysRolePermission, SysPermission
    result = await db.execute(
        select(SysPermission.permission_code)
        .join(SysRolePermission, SysRolePermission.permission_id == SysPermission.id)
        .where(SysRolePermission.role_id == current_user["role_id"])
    )
    codes = set(row[0] for row in result.all())
    if "user:list" not in codes and "user:view_own" in codes:
        if current_user["user_id"] != user_id:
            raise HTTPException(403, "权限不足，只能查看自己的信息")

    result = await db.execute(select(SysUser).where(SysUser.user_id == user_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "用户不存在")
    return obj


@router.post("/users", response_model=SysUserSchema,
             dependencies=[Depends(require_permission('user:create'))])
async def create_user(data: SysUserCreate, db: AsyncSession = Depends(get_db)):
    # 检查用户名是否已存在
    existing = await db.execute(select(SysUser).where(SysUser.username == data.username))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "用户名已存在")
    obj = SysUser(
        role_id=data.role_id,
        username=data.username,
        password=hash_password(data.password),
        real_name=data.real_name,
        phone=data.phone,
        status=data.status,
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.put("/users/{user_id}", response_model=SysUserSchema,
            dependencies=[Depends(require_permission('user:edit'))])
async def update_user(user_id: int, data: SysUserUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysUser).where(SysUser.user_id == user_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "用户不存在")
    update_data = data.model_dump(exclude_unset=True)
    # 密码需要重新哈希
    if "password" in update_data and update_data["password"]:
        update_data["password"] = hash_password(update_data["password"])
    else:
        update_data.pop("password", None)
    for k, v in update_data.items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/users/{user_id}",
               dependencies=[Depends(require_permission('user:delete'))])
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysUser).where(SysUser.user_id == user_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "用户不存在")
    # 同时删除关联的用户档案
    await db.execute(delete(SysUserProfile).where(SysUserProfile.user_id == user_id))
    await db.delete(obj)
    await db.commit()
    return {"detail": "删除成功"}


# ==================== 用户档案 CRUD ====================

@router.get("/user-profiles", response_model=list[SysUserProfileSchema],
            dependencies=[Depends(require_permission('user:list'))])
async def get_user_profiles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysUserProfile))
    return result.scalars().all()


@router.get("/user-profiles/by-user/{user_id}", response_model=SysUserProfileSchema,
            dependencies=[Depends(_require_user_view())])
async def get_user_profile_by_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # user:view_own 只能查看自己
    from app.modules.system.models import SysRolePermission, SysPermission
    result = await db.execute(
        select(SysPermission.permission_code)
        .join(SysRolePermission, SysRolePermission.permission_id == SysPermission.id)
        .where(SysRolePermission.role_id == current_user["role_id"])
    )
    codes = set(row[0] for row in result.all())
    if "user:list" not in codes and "user:view_own" in codes:
        if current_user["user_id"] != user_id:
            raise HTTPException(403, "权限不足，只能查看自己的档案")

    result = await db.execute(
        select(SysUserProfile).where(SysUserProfile.user_id == user_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "用户档案不存在")
    return obj


@router.get("/user-profiles/{profile_id}", response_model=SysUserProfileSchema,
            dependencies=[Depends(require_permission('user:list'))])
async def get_user_profile(profile_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SysUserProfile).where(SysUserProfile.profile_id == profile_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "用户档案不存在")
    return obj


@router.post("/user-profiles", response_model=SysUserProfileSchema,
             dependencies=[Depends(require_permission('user:create'))])
async def create_user_profile(data: SysUserProfileCreate, db: AsyncSession = Depends(get_db)):
    obj = SysUserProfile(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.put("/user-profiles/{profile_id}", response_model=SysUserProfileSchema,
            dependencies=[Depends(require_permission('user:edit'))])
async def update_user_profile(
    profile_id: int, data: SysUserProfileUpdate, db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SysUserProfile).where(SysUserProfile.profile_id == profile_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "用户档案不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/user-profiles/{profile_id}",
               dependencies=[Depends(require_permission('user:delete'))])
async def delete_user_profile(profile_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SysUserProfile).where(SysUserProfile.profile_id == profile_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "用户档案不存在")
    await db.delete(obj)
    await db.commit()
    return {"detail": "删除成功"}
