import bleach

# 富文本允许的html白名单，移除img避免src伪协议风险
ALLOWED_TAGS = [
    'p', 'br', 'b', 'i', 'u', 'strong', 'em',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'a', 'div', 'span'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'div': ['class'],
    'span': ['class']
}

ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


def sanitize_html(content: str | None) -> str | None:
    """清洗富文本HTML，防御存储型XSS，有限保留安全标签"""
    if not content:
        return content

    return bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
        strip_comments=True
    )


def sanitize_text(text: str | None) -> str | None:
    """清洗纯文本：用户名、标题，全部HTML转义，不保留任何标签"""
    if not text:
        return text
    return bleach.clean(
        text,
        tags=[],
        attributes={},
        protocols=[],
        strip=False
    )