from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import ClientDisconnect

from schemas.user import UserCreate, UserRead, UserUpdate
from core.auth import auth_backend, bearer_auth_backend, fastapi_users
from core.config import get_settings
from admin.choices import warm_choices_cache
from core.db import async_session_maker
from core.storage import UPLOAD_DIR, configure_storage
from public.router import router
from api.v1 import router as api_v1_router
from api.v1.auth import router as jwt_auth_router
from admin.admin import admin
from seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Logic ---
    configure_storage()
    print("Application is starting up")
    await seed_database()
    async with async_session_maker() as session:
        await warm_choices_cache(session)

    yield
    # --- Shutdown Logic ---
    # Close connections, flush logs, or release memory
    print("Application is shutting down")


app = FastAPI(lifespan=lifespan)


@app.exception_handler(ClientDisconnect)
async def client_disconnect_handler(request, exc: ClientDisconnect):
    # Client closed connection while request body was being read.
    # Return a quiet response instead of noisy traceback logs.
    return Response(status_code=499)

# CORS configuration — set CORS_ORIGINS in .env for production
_cors_raw = get_settings().cors_origins
_cors_origins = [o.strip() for o in _cors_raw.split(",")] if _cors_raw != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve CSS/JS
app.mount("/static", StaticFiles(directory="static"), name="static")
# Include public routes
app.include_router(router)
# Include API v1 routes
app.include_router(api_v1_router)
# Auth routers — cookie backend (web admin)
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"],
)
# Auth routers — bearer backend (mobile / API)
app.include_router(
    fastapi_users.get_auth_router(bearer_auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
# Custom JWT refresh/logout endpoints
app.include_router(jwt_auth_router)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
# Mount to admin to app
admin.mount_to(app)


if get_settings().environment != "prod":
    @app.get("/debug/storage", tags=["debug"])
    async def debug_storage():
        s = get_settings()
        s3_configured = bool(s.s3_access_key and s.s3_secret_key and s.s3_endpoint and s.s3_bucket)
        return JSONResponse({
            "backend": "s3" if s3_configured else "local",
            "s3_endpoint": s.s3_endpoint or None,
            "s3_bucket": s.s3_bucket or None,
            "s3_region": s.s3_region,
            "local_fallback_dir": None if s3_configured else UPLOAD_DIR,
            "s3_access_key_set": bool(s.s3_access_key),
            "s3_secret_key_set": bool(s.s3_secret_key),
        })
