import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.db import get_db

""" Données de test """
from public.listing_data import homepage_listings


templates = Jinja2Templates(directory="templates")
router = APIRouter()


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
async def get_listing_details(request: Request, session=Depends(get_db)):
    logging.info(f"Home page accessed from {request.client.host}")
    home
    return templates.TemplateResponse(request, "public/pages/properties/details.html")