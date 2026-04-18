import os
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette_admin.contrib.sqlmodel import Admin
from starlette_admin import I18nConfig
from starlette_admin.i18n import SUPPORTED_LOCALES

from schemas.user import UserCreate, UserRead, UserUpdate
from core.auth import auth_backend, fastapi_users
from public.router import router
from admin.admin import admin
from seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Logic ---
    # Initialize DB pools, load ML models, or warm up caches
    print("Application is starting up")
    # Seed the database with initial data if needed
    await seed_database()

    yield
    # --- Shutdown Logic ---
    # Close connections, flush logs, or release memory
    print("Application is shutting down")


app = FastAPI(lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve CSS/JS
app.mount("/static", StaticFiles(directory="static"), name="static")
# Include public routes
app.include_router(router)
# Auth routers
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"],
)
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
