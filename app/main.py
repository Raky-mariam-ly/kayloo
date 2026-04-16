import os
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette_admin.contrib.sqlmodel import Admin
from starlette_admin import I18nConfig
from starlette_admin.i18n import SUPPORTED_LOCALES

from core.auth import get_async_session_context
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
# Mount to admin to app
admin.mount_to(app)
