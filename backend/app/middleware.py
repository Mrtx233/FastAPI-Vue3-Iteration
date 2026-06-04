from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import settings
from app.crypto import encrypt

# 不需要加密的路径前缀（Swagger 文档等）
EXCLUDE_PREFIXES = ("/docs", "/redoc", "/openapi.json")


class EncryptResponseMiddleware(BaseHTTPMiddleware):
    """将 API 的 JSON 响应体整体 AES 加密后返回 {"data": "<密文>"}"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        # 跳过非 JSON 响应和排除路径
        if request.url.path.startswith(EXCLUDE_PREFIXES):
            return response
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return response

        # 读取原始响应体
        body_chunks = []
        async for chunk in response.body_iterator:
            if isinstance(chunk, bytes):
                body_chunks.append(chunk)
            else:
                body_chunks.append(chunk.encode("utf-8"))
        raw_body = b"".join(body_chunks)

        # 对整个 JSON 字符串进行 AES 加密
        encrypted = encrypt(raw_body.decode("utf-8"), settings.AES_SECRET_KEY)

        return JSONResponse(
            content={"data": encrypted},
            status_code=response.status_code,
        )
