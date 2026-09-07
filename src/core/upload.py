"""
文件上传工具：保存头像图片，生成访问URL
"""
import os
import uuid
from pathlib import Path
from fastapi import HTTPException, UploadFile, status

# 允许的图片类型
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}

# 最大文件大小 (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

# 项目根目录 / static / avatars
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = PROJECT_ROOT / "static" / "avatars"


def ensure_upload_dir() -> Path:
    """确保上传目录存在"""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    return UPLOAD_DIR


async def save_avatar(file: UploadFile) -> str:
    """
    保存头像文件，返回可访问的URL路径
    返回格式: /static/avatars/filename.ext
    """
    ensure_upload_dir()

    # 校验文件类型
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的图片格式，仅支持 JPG、PNG、GIF、WebP"
        )

    # 读取文件内容（检查大小）
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图片大小不能超过5MB"
        )

    # 根据content_type生成扩展名
    ext_map = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/webp": ".webp",
    }
    ext = ext_map.get(file.content_type, ".jpg")

    # 生成唯一文件名
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = UPLOAD_DIR / filename

    # 写入文件
    with open(filepath, "wb") as f:
        f.write(content)

    # 返回可访问的URL路径
    return f"/static/avatars/{filename}"
