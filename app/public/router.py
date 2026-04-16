import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.db import get_db


templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, session=Depends(get_db)):
    logging.info(f"Home page accessed from {request.client.host}")
    data = {"message": "Welcome to the Kayloo Web App!"}
    return templates.TemplateResponse(request, "public/index.html", data)
