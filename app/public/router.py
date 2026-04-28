import hashlib
import logging
import os
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from core.db import get_db
from core.config import get_settings
from models.property_view import PropertyView
from repositories.property import PropertyRepository
from repositories.property_view import PropertyViewRepository
from services.property_view import PropertyViewService
from static.text_content import *
import admin.choices as _choices


templates = Jinja2Templates(directory="templates")
router = APIRouter()

PLACEHOLDER_IMAGE = "https://picsum.photos/seed/kayloo/800/600"


# ── Helpers ─────────────────────────────────────────────────────────────────

def _extract_url(raw) -> str | None:
    """Extract a usable image URL from a FileStorageField value."""
    if not raw:
        return None
    if isinstance(raw, dict):
        content_type = raw.get("content_type", "")
        size = raw.get("size", 999999)
        # Seed artefact: text file containing a URL string (~38 bytes, non-image)
        is_seed_text = size <= 200 and not content_type.startswith("image/")

        url = raw.get("url")
        if url and not is_seed_text:
            # Real image on S3/CDN
            return url

        # Local storage fallback
        files = raw.get("files") or []
        if files:
            file_rel = files[0]
            disk_path = os.path.join("static", "uploads", file_rel)
            if is_seed_text:
                # Try to read the stored URL string back from disk
                try:
                    with open(disk_path, "r", errors="replace") as fh:
                        content = fh.read().strip()
                    if content.startswith("http"):
                        return content
                except OSError:
                    pass
                return None
            if os.path.exists(disk_path):
                return f"/static/uploads/{file_rel}"
        path = raw.get("path")
        if path:
            full = os.path.join("static", "uploads", path)
            if os.path.exists(full):
                return f"/static/uploads/{path}"
    if isinstance(raw, str) and raw.startswith("http"):
        return raw
    return None


def _get_image_url(prop) -> str:
    """Return the best image URL for a property, with a deterministic fallback."""
    for img_obj in (prop.images or []):
        url = _extract_url(img_obj.url)
        if url:
            return url
    url = _extract_url(getattr(prop, "image_url", None))
    if url:
        return url
    # Deterministic picsum placeholder based on property ID → stable across requests
    seed = str(prop.id).split("-")[0] if prop.id else "kayloo"
    return f"https://picsum.photos/seed/{seed}/800/600"


def _cover_image_url(prop) -> str:
    """Return the cover image URL (image_url field), with deterministic fallback."""
    url = _extract_url(getattr(prop, "image_url", None))
    if url:
        return url
    seed = str(prop.id).split("-")[0] if prop.id else "kayloo"
    return f"https://picsum.photos/seed/{seed}/800/600"


def _gallery_image_urls(prop) -> list:
    """Return gallery images from PropertyGallery.images (multi-file FileStorageField)."""
    gallery = getattr(prop, "gallery", None)
    if not gallery or not gallery.images:
        return []
    urls = []
    for img in gallery.images:
        url = _extract_url(img)
        if url:
            urls.append(url)
    return urls


def _property_to_listing(prop) -> dict:
    rent_type = (prop.rent_type or "").upper()
    status = (prop.status or "").lower()

    if rent_type == "SALE" or status in ("for_sale", "sold"):
        listing_type = "sale"
    elif rent_type == "RENT_FURNISHED":
        listing_type = "furnished"
    else:
        listing_type = "rent"

    if listing_type == "sale":
        price_val = prop.sale_price or prop.price or 0
        has_period = False
        period = ""
    else:
        price_val = prop.rent_price or prop.price or 0
        has_period = True
        rp = (prop.rental_period or "").lower()
        if rp == "daily":
            period = "/ jour"
        elif rp == "yearly":
            period = "/ an"
        else:
            period = "/ mois"

    price_str = f"{int(price_val):,}".replace(",", " ") if price_val else "—"
    currency = prop.currency or "F CFA"

    return {
        "id": str(prop.id),
        "title": prop.label or prop.code or "Bien immobilier",
        "link": f"/details-annonce?id={prop.id}",
        "bg_image": _get_image_url(prop),
        "is_featured": bool(prop.is_featured),
        "type": listing_type,
        "price": price_str,
        "currency": currency,
        "has_period": has_period,
        "period": period,
        "location": prop.zone or prop.city or prop.address or "",
        "property_type": prop.type or "",
        "bedroom_nbr": prop.bed_room_count,
        "bthroom_nbr": prop.bath_room_count,
        "land_size": int(prop.surface) if prop.surface else None,
        "lat": float(prop.lat) if prop.lat else None,
        "lng": float(prop.lng) if prop.lng else None,
    }


async def _record_view(session: AsyncSession, property_id: UUID, request: Request):
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


# ── Routes ───────────────────────────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, session: AsyncSession = Depends(get_db)):
    repo = PropertyRepository(session)
    props = await repo.search(is_featured=True, limit=10)
    listings = [_property_to_listing(p) for p in props]
    return templates.TemplateResponse(
        request=request,
        name="public/index.html",
        context={
            "carousel_section_data": carousel_homepage_text,
            "listings": listings,
        },
    )


@router.get("/carousel/loadmore", response_class=HTMLResponse)
async def load_more_listings(
    request: Request,
    offset: int = Query(0),
    limit: int = Query(3),
    rent_category: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db),
):
    repo = PropertyRepository(session)
    props = await repo.search(
        is_featured=True,
        rent_category=rent_category,
        type=type,
        skip=offset,
        limit=limit,
    )
    if not props:
        return ""
    listings = [_property_to_listing(p) for p in props]
    return templates.TemplateResponse(
        request=request,
        name="public/workers/_load_more.html",
        context={"listings": listings},
    )


@router.get("/location-bailleur", response_class=HTMLResponse)
async def get_bailleur(request: Request, session: AsyncSession = Depends(get_db)):
    repo = PropertyRepository(session)
    props = await repo.search(is_featured=True, rent_category="rent", limit=10)
    return templates.TemplateResponse(request, "public/pages/location-bailleur.html", context={
        "carousel_section_data": carousel_location_bailleur_text,
        "listings": [_property_to_listing(p) for p in props],
        "carousel_params": "rent_category=rent",
    })


@router.get("/location-locataire", response_class=HTMLResponse)
async def get_locataire(request: Request, session: AsyncSession = Depends(get_db)):
    repo = PropertyRepository(session)
    props = await repo.search(is_featured=True, rent_category="rent", limit=10)
    return templates.TemplateResponse(request, "public/pages/location-locataire.html", context={
        "carousel_section_data": carousel_location_locataire_text,
        "listings": [_property_to_listing(p) for p in props],
        "carousel_params": "rent_category=rent",
    })


@router.get("/vente-acheteur", response_class=HTMLResponse)
async def get_acheteur(request: Request, session: AsyncSession = Depends(get_db)):
    repo = PropertyRepository(session)
    props = await repo.search(is_featured=True, rent_category="sale", limit=10)
    return templates.TemplateResponse(request, "public/pages/vente-acheteur.html", context={
        "carousel_section_data": carousel_vente_acheteur_text,
        "listings": [_property_to_listing(p) for p in props],
        "carousel_params": "rent_category=sale",
    })


@router.get("/vente-vendeur", response_class=HTMLResponse)
async def get_vendeur(request: Request, session: AsyncSession = Depends(get_db)):
    repo = PropertyRepository(session)
    props = await repo.search(is_featured=True, rent_category="sale", limit=10)
    return templates.TemplateResponse(request, "public/pages/vente-vendeur.html", context={
        "carousel_section_data": carousel_vente_vendeur_text,
        "listings": [_property_to_listing(p) for p in props],
        "carousel_params": "rent_category=sale",
    })


@router.get("/construire", response_class=HTMLResponse)
async def get_construire(request: Request, session: AsyncSession = Depends(get_db)):
    repo = PropertyRepository(session)
    props = await repo.search(is_featured=True, type="LAND", rent_category="sale", limit=10)
    return templates.TemplateResponse(request, "public/pages/construire.html", context={
        "carousel_section_data": carousel_construire_text,
        "listings": [_property_to_listing(p) for p in props],
        "carousel_params": "rent_category=sale&type=LAND",
    })


@router.get("/diaspora", response_class=HTMLResponse)
async def get_diaspora(request: Request, session: AsyncSession = Depends(get_db)):
    return templates.TemplateResponse(request, "public/pages/diaspora.html")


@router.get("/agences", response_class=HTMLResponse)
async def get_agencies(request: Request, session: AsyncSession = Depends(get_db)):
    return templates.TemplateResponse(request, "public/pages/partners/listing.html", context={
        "heading": "Nos agences immobilières partenaires",
    })


@router.get("/agents", response_class=HTMLResponse)
async def get_agents(request: Request, session: AsyncSession = Depends(get_db)):
    return templates.TemplateResponse(request, "public/pages/partners/listing.html", context={
        "heading": "Nos agents immobiliers partenaires",
    })


@router.get("/partenaires-construction", response_class=HTMLResponse)
async def get_partners(request: Request, session: AsyncSession = Depends(get_db)):
    return templates.TemplateResponse(request, "public/pages/partners/listing.html", context={
        "heading": "Nos partenaires de construction",
    })


@router.get("/resultats", response_class=HTMLResponse)
async def get_search_result(
    request: Request,
    listing_type: Optional[str] = Query(None),
    property_type: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    max_price: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db),
):
    city_val = city.strip() or None if city else None
    type_val = property_type.strip() or None if property_type else None
    try:
        price_max = float(max_price) if max_price and max_price.strip() else None
    except ValueError:
        price_max = None
    rent_cat = None
    if listing_type == "location":
        rent_cat = "rent"
    elif listing_type in ("vente", "sale"):
        rent_cat = "sale"

    repo = PropertyRepository(session)
    props = await repo.search(city=city_val, type=type_val, price_max=price_max, rent_category=rent_cat, limit=24)
    total = await repo.count_search(city=city_val, type=type_val, price_max=price_max, rent_category=rent_cat)
    cities = await repo.get_distinct_cities()
    listings = [_property_to_listing(p) for p in props]
    return templates.TemplateResponse(
        request=request,
        name="public/pages/properties/search.html",
        context={
            "listings": listings,
            "total": total,
            "cities": cities,
            "property_types": _choices._property_type_choices,
            "google_maps_api_key": get_settings().google_maps_api_key,
        },
    )


@router.get("/details-annonce", response_class=HTMLResponse)
async def get_listing_details(
    request: Request,
    id: UUID | None = Query(None),
    session: AsyncSession = Depends(get_db),
):
    prop = None
    listing = None
    cover_image = PLACEHOLDER_IMAGE
    gallery_images = []
    similar_listings = []

    if id:
        await _record_view(session, id, request)
        repo = PropertyRepository(session)
        prop = await repo.get(id)
        if prop:
            listing = _property_to_listing(prop)
            cover_image = _cover_image_url(prop)
            gallery_images = _gallery_image_urls(prop)
            similar_props = await repo.search(city=prop.city, limit=7)
            similar_listings = [
                _property_to_listing(p) for p in similar_props
                if str(p.id) != str(id)
            ][:6]

    return templates.TemplateResponse(
        request,
        "public/pages/properties/details.html",
        {
            "property": prop,
            "listing": listing,
            "cover_image": cover_image,
            "gallery_images": gallery_images,
            "similar_listings": similar_listings,
        },
    )


@router.get("/cgu", response_class=HTMLResponse)
async def get_CGU(request: Request, session: AsyncSession = Depends(get_db)):
    return templates.TemplateResponse(request, "public/pages/legal/cgu.html", context={})


@router.get("/mot-de-passe-oublie", response_class=HTMLResponse)
async def forgot_password(request: Request):
    return templates.TemplateResponse(request, "public/pages/forgot-password.html", {})


@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password(request: Request):
    return templates.TemplateResponse(request, "public/pages/reset-password.html", {})
