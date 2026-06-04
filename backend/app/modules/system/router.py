from typing import Optional
from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.system.models import (
    SysPermission,
    SysRole,
    SysRolePermission,
    SysUser,
    SysUserProfile,
)

router = APIRouter(prefix="/api/system", tags=["系统管理"])


# ---------- Pydantic Schemas ----------

class SysPermissionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    permission_code: str
    permission_name: str
    menu_path: Optional[str] = None


class SysRoleSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role_code: str
    role_name: str


class SysRolePermissionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role_id: int
    permission_id: int


class SysUserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    role_id: int
    username: str
    password: str
    real_name: Optional[str] = None
    phone: Optional[str] = None
    status: int


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


# ---------- Endpoints ----------

@router.get("/permissions", response_model=list[SysPermissionSchema])
async def get_permissions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysPermission))
    return result.scalars().all()


@router.get("/roles", response_model=list[SysRoleSchema])
async def get_roles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysRole))
    return result.scalars().all()


@router.get("/role-permissions", response_model=list[SysRolePermissionSchema])
async def get_role_permissions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysRolePermission))
    return result.scalars().all()


@router.get("/users", response_model=list[SysUserSchema])
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysUser))
    return result.scalars().all()


@router.get("/user-profiles", response_model=list[SysUserProfileSchema])
async def get_user_profiles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysUserProfile))
    return result.scalars().all()
