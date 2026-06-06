"""
通用文件上传模块
- POST /api/upload/  上传图片文件，返回相对路径
- GET  /api/upload/  列出已上传文件（管理员）
"""
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_permission
from app.core.database import get_db

# 上传目录：backend/uploads/
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# 允许的文件类型
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

router = APIRouter(prefix="/api/upload", tags=["文件上传"])


@router.post("/", dependencies=[Depends(require_permission("file:upload"))])
async def upload_file(file: UploadFile = File(...)):
    """上传单个文件，返回相对路径"""
    # 验证文件类型
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {ext}，允许: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # 读取文件内容并检查大小
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件过大，最大允许 {MAX_FILE_SIZE // (1024*1024)} MB",
        )

    # 生成唯一文件名
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / unique_name

    # 写入磁盘
    with open(file_path, "wb") as f:
        f.write(content)

    relative_url = f"/uploads/{unique_name}"

    return {
        "url": relative_url,
        "original_name": file.filename,
        "size": len(content),
        "content_type": file.content_type,
    }


@router.get("/", dependencies=[Depends(require_permission("file:upload"))])
async def list_uploaded_files():
    """列出已上传的文件"""
    files = []
    for f in sorted(UPLOAD_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if f.is_file():
            stat = f.stat()
            files.append({
                "name": f.name,
                "url": f"/uploads/{f.name}",
                "size": stat.st_size,
                "modified": stat.st_mtime,
            })
    return files


@router.delete("/{filename}",
               dependencies=[Depends(require_permission("file:upload"))])
async def delete_uploaded_file(filename: str):
    """删除指定的已上传文件"""
    file_path = UPLOAD_DIR / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(404, "文件不存在")
    # 安全检查：防止路径遍历
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(400, "非法文件名")
    file_path.unlink()
    return {"detail": "删除成功"}
