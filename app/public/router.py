import hashlib
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from models.property_view import PropertyView
from repositories.property_view import PropertyViewRepository
from services.property_view import PropertyViewService

""" Données de test """
from public.listing_data import homepage_listings


templates = Jinja2Templates(directory="templates")
router = APIRouter()


async def _record_view(session: AsyncSession, property_id: UUID, request: Request):
    """Record a property view using IP + User-Agent hash as session_id."""
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "")
    session_id = hashlib.sha256(f"{ip}:{ua}".encode()).hexdigest()

    service = PropertyViewService(PropertyViewRepository(session))
    view = PropertyView(
        property_id=property_id,
        session_id=session_id,
        ip_address=ip,
        user_agent=ua,
    )
    try:
        await service.record_view(view)
    except Exception:
        logging.warning(f"Failed to record view for property {property_id}", exc_info=True)


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, session=Depends(get_db)):
    logging.info(f"Home page accessed from {request.client.host}")
    home
    return templates.TemplateResponse(request, "public/index.html", context={
        "listings": homepage_listings
    })

@router.get("/location-bailleur", response_class=HTMLResponse)
async def get_bailleur(request: Request, session=Depends(get_db)):
    logging.info(f"Home page accessed from {request.client.host}")
    home
    return templates.TemplateResponse(request, "public/pages/location-bailleur.html", context={
        "listings": homepage_listings
    })

@router.get("/location-locataire", response_class=HTMLResponse)
async def get_locataire(request: Request, session=Depends(get_db)):
    logging.info(f"Home page accessed from {request.client.host}")
    home
    return templates.TemplateResponse(request, "public/pages/location-locataire.html", context={
        "listings": homepage_listings
    })

@router.get("/vente-acheteur", response_class=HTMLResponse)
async def get_acheteur(request: Request, session=Depends(get_db)):
    logging.info(f"Home page accessed from {request.client.host}")
    home
    return templates.TemplateResponse(request, "public/pages/vente-acheteur.html", context={
        "listings": homepage_listings
    })

@router.get("/vente-vendeur", response_class=HTMLResponse)
async def get_vendeur(request: Request, session=Depends(get_db)):
    logging.info(f"Home page accessed from {request.client.host}")
    home
    return templates.TemplateResponse(request, "public/pages/vente-vendeur.html", context={
        "listings": homepage_listings
    })

@router.get("/construire", response_class=HTMLResponse)
async def get_construire(request: Request, session=Depends(get_db)):
    logging.info(f"Home page accessed from {request.client.host}")
    home
    return templates.TemplateResponse(request, "public/pages/construire.html", context={
        "listings": homepage_listings
    })

@router.get("/diaspora", response_class=HTMLResponse)
async def get_diaspora(request: Request, session=Depends(get_db)):
    logging.info(f"Home page accessed from {request.client.host}")
    home
    return templates.TemplateResponse(request, "public/pages/diaspora.html")

@router.get("/agences", response_class=HTMLResponse)
async def get_agencies(request: Request, session=Depends(get_db)):
    logging.info(f"Home page accessed from {request.client.host}")
    home
    return templates.TemplateResponse(request, "public/pages/partners/listing.html", context={
        "heading": "Nos agences immobilières partenaires"
    })

@router.get("/agents", response_class=HTMLResponse)
async def get_agents(request: Request, session=Depends(get_db)):
    logging.info(f"Home page accessed from {request.client.host}")
    home
    return templates.TemplateResponse(request, "public/pages/partners/listing.html", context={
        "heading": "Nos agents immobiliers partenaires"
    })


@router.get("/partenaires-construction", response_class=HTMLResponse)
async def get_partners(request: Request, session=Depends(get_db)):
    logging.info(f"Home page accessed from {request.client.host}")
    home
    return templates.TemplateResponse(request, "public/pages/partners/listing.html", context={
        "heading": "Nos partenaires de construction"
    })

@router.get("/annonces", response_class=HTMLResponse)
async def get_search_result(request: Request, session=Depends(get_db)):
    logging.info(f"Home page accessed from {request.client.host}")
    home
    return templates.TemplateResponse(request, "public/pages/properties/listing.html")

@router.get("/details-annonce", response_class=HTMLResponse)
async def get_listing_details(
    request: Request,
    id: UUID | None = Query(None),
    session: AsyncSession = Depends(get_db),
):
    logging.info(f"Property details accessed from {request.client.host}")
    if id:
        await _record_view(session, id, request)
    return templates.TemplateResponse(request, "public/pages/properties/details.html")