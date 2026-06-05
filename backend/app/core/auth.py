from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db

# ---------- 密码工具 ----------

def hash_password(plaintext: str) -> str:
    """使用 bcrypt 生成密码哈希"""
    return bcrypt.hashpw(plaintext.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plaintext: str, hashed: str) -> bool:
    """比对明文密码与 bcrypt 哈希"""
    return bcrypt.checkpw(plaintext.encode("utf-8"), hashed.encode("utf-8"))


# ---------- JWT 工具 ----------

def create_access_token(user_id: int, role_id: int, username: str) -> str:
    """生成 JWT Token，有效期 2 小时"""
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),
        "role_id": role_id,
        "username": username,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """解码并验证 JWT Token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ---------- FastAPI 鉴权依赖 ----------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/system/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    从请求头 Authorization: Bearer <token> 中提取并验证 JWT，
    返回当前用户信息 {"user_id", "role_id", "username"}。
    """
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 中缺少用户信息",
        )

    # 查询用户是否存在且状态正常
    from app.modules.system.models import SysUser
    result = await db.execute(select(SysUser).where(SysUser.user_id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None or user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用",
        )

    return {
        "user_id": user.user_id,
        "role_id": user.role_id,
        "username": user.username,
    }


# ---------- RBAC 权限校验 ----------

def require_permission(required_code: str):
    """
    权限校验依赖工厂。
    用法: dependencies=[Depends(require_permission('user:list'))]
    查询 sys_role_permission + sys_permission，校验当前用户角色是否拥有指定权限。
    """
    async def checker(
        current_user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        from app.modules.system.models import SysRolePermission, SysPermission

        # 查询当前角色拥有的所有权限编码
        result = await db.execute(
            select(SysPermission.permission_code)
            .join(SysRolePermission, SysRolePermission.permission_id == SysPermission.id)
            .where(SysRolePermission.role_id == current_user["role_id"])
        )
        user_perm_codes = set(row[0] for row in result.all())

        if required_code not in user_perm_codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要: {required_code}",
            )

        return current_user

    return checker
