from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings
from app.core.crypto import encrypt

EXCLUDE_PREFIXES = ("/docs", "/redoc", "/openapi.json")


class EncryptResponseMiddleware(BaseHTTPMiddleware):
    """Encrypt API JSON response bodies with AES, returning {"data": "<ciphertext>"}"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        if request.url.path.startswith(EXCLUDE_PREFIXES):
            return response
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return response

        body_chunks = []
        async for chunk in response.body_iterator:
            if isinstance(chunk, bytes):
                body_chunks.append(chunk)
            else:
                body_chunks.append(chunk.encode("utf-8"))
        raw_body = b"".join(body_chunks)

        encrypted = encrypt(raw_body.decode("utf-8"), settings.AES_SECRET_KEY)

        return JSONResponse(
            content={"data": encrypted},
            status_code=response.status_code,
        )
