"""
AI 对话接口：调用大模型辅助写作，回复可一键填入日记/目标表单
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from api.deps import get_current_user
from models.models import Main_User
from core.config import settings
from core.logger import logger
import httpx

router = APIRouter(prefix="/ai", tags=["AI 助手"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用户输入的消息")
    context: str = Field("", description="当前场景：diary / goal / profile")


class ChatResponse(BaseModel):
    reply: str


# 系统提示词：根据场景调整写作风格
SYSTEM_PROMPT = """你是「自白书」个人成长记录系统的 AI 写作助手。
请根据用户的需求，帮助用户撰写日记、目标描述或个人介绍。
要求：
1. 语气真诚、贴近日常，不要太书面化
2. 日记要有画面感和情绪，目标要具体可执行
3. 直接输出正文内容，不要加"好的"、"以下是..."等客套话
4. 如果用户要求生成标题，控制在 15 字以内
"""


@router.post("/chat", response_model=ChatResponse)
async def chat(
    data: ChatRequest,
    current_user: Main_User = Depends(get_current_user)
):
    """与 AI 对话，返回写作建议"""
    if not settings.AI_API_KEY:
        raise HTTPException(status_code=503, detail="AI 服务未配置 API Key，请联系管理员")

    # 根据场景微调提示词
    scene_hint = {
        "diary": "当前用户正在写日记，请输出一篇日记正文。",
        "goal": "当前用户正在制定目标，请输出一段具体、可执行的目标描述。",
        "profile": "当前用户正在编辑个人资料，请输出一段简短的自我介绍。",
    }.get(data.context, "")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + scene_hint},
        {"role": "user", "content": data.message},
    ]

    payload = {
        "model": settings.AI_MODEL,
        "messages": messages,
        "temperature": 0.8,
        "max_tokens": 1024,
    }

    headers = {
        "Authorization": f"Bearer {settings.AI_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT) as client:
            resp = await client.post(
                f"{settings.AI_BASE_URL}/chat/completions",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            result = resp.json()
            reply = result["choices"][0]["message"]["content"].strip()
    except httpx.HTTPStatusError as e:
        logger.error(f"AI 接口返回错误: {e.response.status_code} {e.response.text}")
        raise HTTPException(status_code=502, detail=f"AI 服务错误: {e.response.status_code}")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI 服务响应超时")
    except Exception as e:
        logger.error(f"AI 调用异常: {e}")
        raise HTTPException(status_code=502, detail="AI 服务不可用")

    return ChatResponse(reply=reply)
