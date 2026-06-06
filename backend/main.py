from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.database import engine
from app.core.middleware import EncryptResponseMiddleware
from app.modules import Base

# 导入所有模块的 models，确保 create_all 能识别全部表
from app.modules.system import models as _sys_models  # noqa: F401
from app.modules.slogan import models as _slogan_models  # noqa: F401
from app.modules.activity import models as _activity_models  # noqa: F401
from app.modules.store import models as _store_models  # noqa: F401
from app.modules.course import models as _course_models  # noqa: F401
from app.modules.action import models as _action_models  # noqa: F401

# 导入所有路由
from app.modules.system.router import router as system_router
from app.modules.slogan.router import router as slogan_router
from app.modules.activity.router import router as activity_router
from app.modules.store.router import router as store_router
from app.modules.course.router import router as course_router
from app.modules.action.router import router as action_router
from app.modules.upload.router import router as upload_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Fitness Management API", version="0.2.0", lifespan=lifespan)

app.add_middleware(EncryptResponseMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system_router)
app.include_router(slogan_router)
app.include_router(activity_router)
app.include_router(store_router)
app.include_router(course_router)
app.include_router(action_router)
app.include_router(upload_router)

# 挂载上传文件静态服务（放在最后，不影响 API 路由）
_uploads_dir = Path(__file__).parent / "uploads"
_uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(_uploads_dir)), name="uploads")
