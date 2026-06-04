from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


# ---------- 用户相关 ----------

class UserCreate(BaseModel):
    username: str = Field(max_length=64, description="用户名")
    password: str = Field(max_length=128, description="密码")
    real_name: Optional[str] = Field(default=None, max_length=64, description="真实姓名")
    phone: Optional[str] = Field(default=None, max_length=20, description="手机号")
    status: int = Field(default=1, description="状态")


class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None, max_length=64, description="用户名")
    password: Optional[str] = Field(default=None, max_length=128, description="密码")
    real_name: Optional[str] = Field(default=None, max_length=64, description="真实姓名")
    phone: Optional[str] = Field(default=None, max_length=20, description="手机号")
    status: Optional[int] = Field(default=None, description="状态")


class UserResponse(BaseModel):
    """对外响应模型，返回 AES 加密后的密码，由前端负责解密"""
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    username: str
    password: str
    real_name: Optional[str]
    phone: Optional[str]
    status: int


# ---------- 登录相关 ----------

class UserLogin(BaseModel):
    username: str = Field(max_length=64, description="用户名")
    password: str = Field(max_length=128, description="明文密码")


class LoginResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserResponse] = None


# ---------- 分页相关 ----------

class PageResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
