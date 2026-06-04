from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.crypto import decrypt, encrypt
from app.database import get_db
from app.models import SysUser
from app.schemas import (
    LoginResponse,
    PageResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)

router = APIRouter(prefix="/api/users", tags=["用户管理"])


@router.post("", response_model=UserResponse)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """创建用户，密码使用 AES 加密存储"""
    data = user_in.model_dump()
    data["password"] = encrypt(data["password"], settings.AES_SECRET_KEY)
    user = SysUser(**data)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("", response_model=PageResponse[UserResponse])
async def list_users(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=10, ge=1, le=100, description="每页条数"),
    db: AsyncSession = Depends(get_db),
):
    """分页查询用户列表（不返回密码）"""
    total_result = await db.execute(select(func.count()).select_from(SysUser))
    total = total_result.scalar_one()

    offset = (page - 1) * page_size
    users_result = await db.execute(
        select(SysUser).offset(offset).limit(page_size)
    )
    users = users_result.scalars().all()

    return PageResponse(items=users, total=total, page=page, page_size=page_size)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """根据 ID 查询用户（不返回密码）"""
    user = await db.get(SysUser, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_in: UserUpdate, db: AsyncSession = Depends(get_db)):
    """更新用户信息，若传入密码则 AES 加密后存储"""
    user = await db.get(SysUser, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    update_data = user_in.model_dump(exclude_unset=True)
    # 如果更新中包含密码，先加密再写入
    if "password" in update_data and update_data["password"] is not None:
        update_data["password"] = encrypt(update_data["password"], settings.AES_SECRET_KEY)
    for key, value in update_data.items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """删除用户"""
    user = await db.get(SysUser, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    await db.delete(user)
    await db.commit()
    return {"message": "删除成功"}


# ---------- 登录验证 ----------

@router.post("/login", response_model=LoginResponse)
async def login(login_in: UserLogin, db: AsyncSession = Depends(get_db)):
    """用户登录：从数据库取出加密密码，解密后与明文比对"""
    result = await db.execute(select(SysUser).where(SysUser.username == login_in.username))
    user = result.scalar_one_or_none()
    if not user:
        return LoginResponse(success=False, message="用户不存在")

    try:
        decrypted_pwd = decrypt(user.password, settings.AES_SECRET_KEY)
    except Exception:
        return LoginResponse(success=False, message="密码解密失败，请联系管理员")

    if decrypted_pwd != login_in.password:
        return LoginResponse(success=False, message="密码错误")

    return LoginResponse(success=True, message="登录成功", user=UserResponse.model_validate(user))
