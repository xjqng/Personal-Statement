"""
日记业务层：存在判断、权限校验，不写SQL
"""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Main_User, Diary
from crud.diaries import create_diary, get_diary_by_id, list_diaries_by_user_id, update_diary, delete_diary
from schemas.diaries import DiaryCreate, DiaryUpdate, DiaryResponse
from core.logger import logger
from core.xxs import sanitize_html, sanitize_text



async def create_diary_service(
    db: AsyncSession,
    obj_in: DiaryCreate,
    current_user: Main_User
) -> DiaryResponse:
    # ========= XSS清洗在这里！保存数据库之前 =========
    safe_title = sanitize_text(obj_in.title)       # 标题纯文本，全部转义
    safe_content = sanitize_html(obj_in.content)   # 正文富文本，保留安全标签

    # 把清洗后的值传给crud，这里我直接构造新schema或者传字典
    # 方案1：直接覆盖对象字段（Pydantic允许）
    obj_in.title = safe_title
    obj_in.content = safe_content

    db_obj = await create_diary(db, obj_in, main_user_id=current_user.id)
    logger.info(f"用户[{current_user.id}] 创建日记成功, diary_id={db_obj.id}")
    return DiaryResponse.model_validate(db_obj)


async def get_diary_detail_service(
    db: AsyncSession,
    diary_id: int,
    current_user: Main_User
) -> DiaryResponse:
    diary = await get_diary_by_id(db, diary_id)
    if not diary:
        logger.warning(f"用户[{current_user.id}] 访问不存在的日记 diary_id={diary_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="日记不存在")
    # 权限校验：只能访问自己的日记
    if diary.user_id != current_user.id:
        logger.warning(f"用户[{current_user.id}] 越权尝试访问他人日记 diary_id={diary_id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该日记")
    logger.info(f"用户[{current_user.id}] 查看日记详情 diary_id={diary_id}")
    return DiaryResponse.model_validate(diary)


async def list_my_diaries_service(
    db: AsyncSession,
    current_user: Main_User,
    skip: int = 0,
    limit: int = 100
) -> list[DiaryResponse]:
    diary_list = await list_diaries_by_user_id(db, current_user.id, skip=skip, limit=limit)
    logger.info(f"用户[{current_user.id}] 查询自己日记列表 skip={skip}, limit={limit}, 数量={len(diary_list)}")
    return [DiaryResponse.model_validate(item) for item in diary_list]


async def update_diary_service(
    db: AsyncSession,
    diary_id: int,
    obj_in: DiaryUpdate,
    current_user: Main_User
) -> DiaryResponse:
    diary = await get_diary_by_id(db, diary_id)
    if not diary:
        logger.warning(f"用户[{current_user.id}] 修改不存在日记 diary_id={diary_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="日记不存在")
    
    if diary.user_id != current_user.id:
        logger.warning(f"用户[{current_user.id}] 越权尝试修改他人日记 diary_id={diary_id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权修改该日记")
    
    # 修改也要XSS清洗！
    if obj_in.title is not None:
        obj_in.title = sanitize_text(obj_in.title)
    if obj_in.content is not None:
        obj_in.content = sanitize_html(obj_in.content)

    updated_obj = await update_diary(db, diary, obj_in)
    logger.info(f"用户[{current_user.id}] 修改日记成功 diary_id={diary_id}")
    return DiaryResponse.model_validate(updated_obj)


async def delete_diary_service(
    db: AsyncSession,
    diary_id: int,
    current_user: Main_User
) -> None:
    diary = await get_diary_by_id(db, diary_id)
    if not diary:
        logger.warning(f"用户[{current_user.id}] 删除不存在日记 diary_id={diary_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="日记不存在")
    
    if diary.user_id != current_user.id:
        logger.warning(f"用户[{current_user.id}] 越权尝试删除他人日记 diary_id={diary_id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除该日记")
    
    await delete_diary(db, diary)
    logger.info(f"用户[{current_user.id}] 删除日记成功 diary_id={diary_id}")
