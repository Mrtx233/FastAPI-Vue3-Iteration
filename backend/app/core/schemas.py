"""
通用分页响应模型与查询辅助工具
"""
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class PaginatedResponse(BaseModel):
    """通用分页响应结构"""
    model_config = ConfigDict(from_attributes=True)

    items: list[Any]
    total: int
    page: int
    page_size: int


async def paginated_query(
    db: AsyncSession,
    model,
    *,
    page: int = 1,
    page_size: int = 20,
    keyword: str | None = None,
    keyword_fields: list | None = None,
    status_field=None,
    status_value: int | str | None = None,
    base_filter=None,
):
    """
    执行带分页、关键字搜索、状态过滤的查询。

    Args:
        db: 数据库会话
        model: SQLAlchemy ORM 模型
        page: 当前页码 (从 1 开始)
        page_size: 每页条数
        keyword: 搜索关键字
        keyword_fields: 需要搜索的模型字段列表 (如 [SysUser.username, SysUser.real_name])
        status_field: 状态字段 (如 SysUser.status)
        status_value: 状态过滤值
        base_filter: 额外基础过滤条件 (SQLAlchemy BinaryExpression)
    Returns:
        PaginatedResponse 实例
    """
    query = select(model)
    count_query = select(func.count()).select_from(model)

    # 关键字搜索
    if keyword and keyword_fields:
        from sqlalchemy import or_
        like_conditions = [
            field.like(f"%{keyword}%") for field in keyword_fields
        ]
        keyword_filter = or_(*like_conditions)
        query = query.where(keyword_filter)
        count_query = count_query.where(keyword_filter)

    # 状态过滤
    if status_field is not None and status_value is not None:
        query = query.where(status_field == status_value)
        count_query = count_query.where(status_field == status_value)

    # 额外基础过滤
    if base_filter is not None:
        query = query.where(base_filter)
        count_query = count_query.where(base_filter)

    # 总数
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 分页
    offset = (max(1, page) - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
