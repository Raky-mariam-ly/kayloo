"""
Test data seeder for agencies, agents, properties and property images.

Generates:
- 5 agencies across SN, CI, GN
- 5 agents (one per user per agency)
- 40 properties with realistic West African real estate data
- 3-5 images per property (~160 images) using picsum.photos placeholders

Run via: seed_database() -> seed_properties_data()
Or standalone: python seed_properties.py
"""
import asyncio
import random
import uuid
from datetime import date, timedelta
from decimal import Decimal

import sqlalchemy
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import get_async_session_context, User
from models.agency import Agency
from models.agent import Agent
from models.property import Property
from models.property_image import PropertyImage


# ── Agency data ──
AGENCIES = [
    {
        "name": "Kayloo Immobilier Dakar",
        "country": "SN",
        "email": "contact@kayloo-dakar.sn",
        "phone_number": "+221 33 820 10 10",
        "siteweb_url": "https://kayloo-dakar.sn",
        "whatsapp_url": "https://wa.me/221338201010",
        "facebook_url": "https://facebook.com/kayloodakar",
        "instagram_url": "https://instagram.com/kayloodakar",
        "is_active": True,
    },
    {
        "name": "Sepro Habitat",
        "country": "SN",
        "email": "info@sepro-habitat.sn",
        "phone_number": "+221 33 821 20 20",
        "siteweb_url": "https://sepro-habitat.sn",
        "whatsapp_url": "https://wa.me/221338212020",
        "is_active": True,
    },
    {
        "name": "Kayloo Abidjan",
        "country": "CI",
        "email": "contact@kayloo-abidjan.ci",
        "phone_number": "+225 27 22 40 50 60",
        "siteweb_url": "https://kayloo-abidjan.ci",
        "facebook_url": "https://facebook.com/kaylooabidjan",
        "is_active": True,
    },
    {
        "name": "Kayloo Conakry",
        "country": "GN",
        "email": "contact@kayloo-conakry.gn",
        "phone_number": "+224 622 30 40 50",
        "is_active": True,
    },
    {
        "name": "Prestige Immo Dakar",
        "country": "SN",
        "email": "contact@prestige-immo.sn",
        "phone_number": "+221 33 860 70 80",
        "siteweb_url": "https://prestige-immo.sn",
        "instagram_url": "https://instagram.com/prestigeimmo",
        "tiktok_url": "https://tiktok.com/@prestigeimmo",
        "is_active": True,
    },
]

# ── Property templates ──
PROPERTY_TEMPLATES = [
    # Dakar — Apartments
    {"label": "Appartement F3 standing — Almadies", "type": "F3", "status": "for_rent", "rent_type": "RENT_EMPTY", "usage": "residential", "country": "SN", "city": "Dakar", "zone": "Almadies",
        "bed_room_count": 2, "bath_room_count": 1, "kitchen_count": 1, "living_room_count": 1, "surface": 85, "rent_price": 450000, "price": 450000, "base_price_type": "per_month"},
    {"label": "Studio meublé — Ngor Virage", "type": "F2", "status": "for_rent", "rent_type": "RENT_FURNISHED", "usage": "residential", "country": "SN", "city": "Dakar", "zone": "Ngor",
        "bed_room_count": 1, "bath_room_count": 1, "kitchen_count": 1, "living_room_count": 0, "surface": 35, "rent_price": 250000, "price": 250000, "base_price_type": "per_month"},
    {"label": "Appartement F4 vue mer — Mermoz", "type": "F4", "status": "for_rent", "rent_type": "RENT_EMPTY", "usage": "residential", "country": "SN", "city": "Dakar", "zone": "Mermoz",
        "bed_room_count": 3, "bath_room_count": 2, "kitchen_count": 1, "living_room_count": 1, "surface": 120, "rent_price": 700000, "price": 700000, "base_price_type": "per_month"},
    {"label": "Appartement F3 rénové — Liberté 6", "type": "F3", "status": "for_rent", "rent_type": "RENT_EMPTY", "usage": "residential", "country": "SN", "city": "Dakar", "zone": "Liberté 6",
        "bed_room_count": 2, "bath_room_count": 1, "kitchen_count": 1, "living_room_count": 1, "surface": 75, "rent_price": 350000, "price": 350000, "base_price_type": "per_month"},
    {"label": "Appartement F5 familial — Fann Résidence", "type": "F5", "status": "for_rent", "rent_type": "RENT_EMPTY", "usage": "residential", "country": "SN", "city": "Dakar", "zone": "Fann",
        "bed_room_count": 4, "bath_room_count": 2, "kitchen_count": 1, "living_room_count": 2, "surface": 160, "rent_price": 900000, "price": 900000, "base_price_type": "per_month"},
    {"label": "Studio meublé — Plateau", "type": "F2", "status": "rented", "rent_type": "RENT_FURNISHED", "usage": "residential", "country": "SN", "city": "Dakar", "zone": "Plateau",
        "bed_room_count": 1, "bath_room_count": 1, "kitchen_count": 1, "living_room_count": 0, "surface": 40, "rent_price": 300000, "price": 300000, "base_price_type": "per_month"},
    # Dakar — Villas
    {"label": "Villa 5 chambres avec piscine — Almadies", "type": "VILLA", "status": "for_sale", "rent_type": "SALE", "usage": "residential", "country": "SN", "city": "Dakar",
        "zone": "Almadies", "bed_room_count": 5, "bath_room_count": 4, "kitchen_count": 2, "living_room_count": 2, "surface": 450, "sale_price": 350000000, "price": 350000000},
    {"label": "Villa 4 chambres — Ouakam", "type": "VILLA", "status": "for_sale", "rent_type": "SALE", "usage": "residential", "country": "SN", "city": "Dakar",
        "zone": "Ouakam", "bed_room_count": 4, "bath_room_count": 3, "kitchen_count": 1, "living_room_count": 2, "surface": 320, "sale_price": 200000000, "price": 200000000},
    {"label": "Villa R+1 — Sacré-Cœur", "type": "VILLA", "status": "for_sale", "rent_type": "SALE", "usage": "residential", "country": "SN", "city": "Dakar",
        "zone": "Sacré-Cœur", "bed_room_count": 6, "bath_room_count": 4, "kitchen_count": 2, "living_room_count": 2, "surface": 500, "sale_price": 450000000, "price": 450000000},
    {"label": "Villa bord de mer — Ngor", "type": "VILLA", "status": "reserved", "rent_type": "SALE", "usage": "residential", "country": "SN", "city": "Dakar",
        "zone": "Ngor", "bed_room_count": 4, "bath_room_count": 3, "kitchen_count": 1, "living_room_count": 2, "surface": 380, "sale_price": 500000000, "price": 500000000},
    # Dakar — Commercial
    {"label": "Bureau open-space — Plateau", "type": "OFFICE", "status": "for_rent", "rent_type": "RENT_EMPTY", "usage": "office", "country": "SN", "city": "Dakar", "zone": "Plateau",
        "bed_room_count": 0, "bath_room_count": 2, "kitchen_count": 0, "living_room_count": 0, "surface": 200, "rent_price": 1500000, "price": 1500000, "base_price_type": "per_month"},
    {"label": "Magasin — Médina", "type": "MAGASIN", "status": "for_rent", "rent_type": "RENT_EMPTY", "usage": "commercial", "country": "SN", "city": "Dakar", "zone": "Médina",
        "bed_room_count": 0, "bath_room_count": 1, "kitchen_count": 0, "living_room_count": 0, "surface": 60, "rent_price": 400000, "price": 400000, "base_price_type": "per_month"},
    {"label": "Plateau de bureaux — Point E", "type": "OFFICE", "status": "for_rent", "rent_type": "RENT_EMPTY", "usage": "office", "country": "SN", "city": "Dakar", "zone": "Point E",
        "bed_room_count": 0, "bath_room_count": 3, "kitchen_count": 1, "living_room_count": 0, "surface": 350, "rent_price": 2500000, "price": 2500000, "base_price_type": "per_month"},
    # Dakar — Terrain
    {"label": "Terrain 300m² — Diamniadio", "type": "LAND", "status": "for_sale", "rent_type": "SALE", "usage": "land", "country": "SN", "city": "Dakar",
        "zone": "Diamniadio", "bed_room_count": 0, "bath_room_count": 0, "kitchen_count": 0, "living_room_count": 0, "surface": 300, "sale_price": 18000000, "price": 18000000},
    {"label": "Terrain 500m² viabilisé — Rufisque", "type": "LAND", "status": "for_sale", "rent_type": "SALE", "usage": "land", "country": "SN", "city": "Dakar",
        "zone": "Rufisque", "bed_room_count": 0, "bath_room_count": 0, "kitchen_count": 0, "living_room_count": 0, "surface": 500, "sale_price": 30000000, "price": 30000000},
    {"label": "Terrain 1000m² — Lac Rose", "type": "LAND", "status": "for_sale", "rent_type": "SALE", "usage": "land", "country": "SN", "city": "Dakar", "zone": "Lac Rose",
        "bed_room_count": 0, "bath_room_count": 0, "kitchen_count": 0, "living_room_count": 0, "surface": 1000, "sale_price": 45000000, "price": 45000000},
    # Dakar — Duplex / Parking
    {"label": "Duplex 4 chambres — Mamelles", "type": "DUPLEX", "status": "for_sale", "rent_type": "SALE", "usage": "residential", "country": "SN", "city": "Dakar",
        "zone": "Mamelles", "bed_room_count": 4, "bath_room_count": 3, "kitchen_count": 1, "living_room_count": 2, "surface": 220, "sale_price": 180000000, "price": 180000000},
    {"label": "Parking sécurisé — Plateau", "type": "PARKING", "status": "for_rent", "rent_type": "RENT_EMPTY", "usage": "commercial", "country": "SN", "city": "Dakar", "zone": "Plateau",
        "bed_room_count": 0, "bath_room_count": 0, "kitchen_count": 0, "living_room_count": 0, "surface": 15, "rent_price": 50000, "price": 50000, "base_price_type": "per_month"},
    # Saly / Mbour
    {"label": "Villa pieds dans l'eau — Saly", "type": "VILLA", "status": "for_sale", "rent_type": "SALE", "usage": "residential", "country": "SN", "city": "Mbour",
        "zone": "Saly", "bed_room_count": 3, "bath_room_count": 2, "kitchen_count": 1, "living_room_count": 1, "surface": 250, "sale_price": 120000000, "price": 120000000},
    {"label": "Appartement F3 — Saly Portudal", "type": "F3", "status": "for_rent", "rent_type": "RENT_FURNISHED", "usage": "residential", "country": "SN", "city": "Mbour", "zone": "Saly",
        "bed_room_count": 2, "bath_room_count": 1, "kitchen_count": 1, "living_room_count": 1, "surface": 80, "rent_price": 35000, "price": 35000, "base_price_type": "per_night"},
    # Saint-Louis
    {"label": "Maison coloniale rénovée — Île de Saint-Louis", "type": "VILLA", "status": "for_sale", "rent_type": "SALE", "usage": "residential", "country": "SN", "city": "Saint-Louis",
        "zone": "Île", "bed_room_count": 4, "bath_room_count": 2, "kitchen_count": 1, "living_room_count": 2, "surface": 280, "sale_price": 95000000, "price": 95000000},
    # Abidjan
    {"label": "Appartement F4 — Cocody Riviera", "type": "F4", "status": "for_rent", "rent_type": "RENT_EMPTY", "usage": "residential", "country": "CI", "city": "Abidjan", "zone": "Cocody Riviera",
        "bed_room_count": 3, "bath_room_count": 2, "kitchen_count": 1, "living_room_count": 1, "surface": 130, "rent_price": 500000, "price": 500000, "base_price_type": "per_month"},
    {"label": "Villa duplex — Cocody Angré", "type": "DUPLEX", "status": "for_sale", "rent_type": "SALE", "usage": "residential", "country": "CI", "city": "Abidjan",
        "zone": "Cocody Angré", "bed_room_count": 5, "bath_room_count": 3, "kitchen_count": 2, "living_room_count": 2, "surface": 400, "sale_price": 280000000, "price": 280000000},
    {"label": "Bureau — Plateau Abidjan", "type": "OFFICE", "status": "for_rent", "rent_type": "RENT_EMPTY", "usage": "office", "country": "CI", "city": "Abidjan", "zone": "Plateau",
        "bed_room_count": 0, "bath_room_count": 2, "kitchen_count": 0, "living_room_count": 0, "surface": 150, "rent_price": 800000, "price": 800000, "base_price_type": "per_month"},
    {"label": "Appartement F3 meublé — Marcory", "type": "F3", "status": "for_rent", "rent_type": "RENT_FURNISHED", "usage": "residential", "country": "CI", "city": "Abidjan", "zone": "Marcory",
        "bed_room_count": 2, "bath_room_count": 1, "kitchen_count": 1, "living_room_count": 1, "surface": 70, "rent_price": 350000, "price": 350000, "base_price_type": "per_month"},
    {"label": "Terrain 600m² — Bingerville", "type": "LAND", "status": "for_sale", "rent_type": "SALE", "usage": "land", "country": "CI", "city": "Abidjan",
        "zone": "Bingerville", "bed_room_count": 0, "bath_room_count": 0, "kitchen_count": 0, "living_room_count": 0, "surface": 600, "sale_price": 25000000, "price": 25000000},
    {"label": "Villa 3 chambres — Assinie", "type": "VILLA", "status": "for_sale", "rent_type": "SALE", "usage": "residential", "country": "CI", "city": "Grand-Bassam",
        "zone": "Assinie", "bed_room_count": 3, "bath_room_count": 2, "kitchen_count": 1, "living_room_count": 1, "surface": 200, "sale_price": 90000000, "price": 90000000},
    # Conakry
    {"label": "Appartement F3 — Kaloum", "type": "F3", "status": "for_rent", "rent_type": "RENT_EMPTY", "usage": "residential", "country": "GN", "city": "Conakry", "zone": "Kaloum",
        "bed_room_count": 2, "bath_room_count": 1, "kitchen_count": 1, "living_room_count": 1, "surface": 75, "rent_price": 4000000, "price": 4000000, "base_price_type": "per_month"},
    {"label": "Villa — Kipé", "type": "VILLA", "status": "for_sale", "rent_type": "SALE", "usage": "residential", "country": "GN", "city": "Conakry", "zone": "Kipé",
        "bed_room_count": 4, "bath_room_count": 2, "kitchen_count": 1, "living_room_count": 2, "surface": 300, "sale_price": 1500000000, "price": 1500000000},
    {"label": "Bureau — Centre-ville Conakry", "type": "OFFICE", "status": "for_rent", "rent_type": "RENT_EMPTY", "usage": "office", "country": "GN", "city": "Conakry", "zone": "Kaloum",
        "bed_room_count": 0, "bath_room_count": 1, "kitchen_count": 0, "living_room_count": 0, "surface": 100, "rent_price": 5000000, "price": 5000000, "base_price_type": "per_month"},
    {"label": "Terrain 400m² — Lambanyi", "type": "LAND", "status": "for_sale", "rent_type": "SALE", "usage": "land", "country": "GN", "city": "Conakry", "zone": "Lambanyi",
        "bed_room_count": 0, "bath_room_count": 0, "kitchen_count": 0, "living_room_count": 0, "surface": 400, "sale_price": 800000000, "price": 800000000},
    # More Dakar variety
    {"label": "Duplex de luxe — Corniche Ouest", "type": "DUPLEX", "status": "for_sale", "rent_type": "SALE", "usage": "residential", "country": "SN", "city": "Dakar",
        "zone": "Corniche", "bed_room_count": 5, "bath_room_count": 4, "kitchen_count": 2, "living_room_count": 2, "surface": 350, "sale_price": 550000000, "price": 550000000},
    {"label": "Appartement F3 — Yoff Virage", "type": "F3", "status": "free", "rent_type": "RENT_EMPTY", "usage": "residential", "country": "SN", "city": "Dakar", "zone": "Yoff",
        "bed_room_count": 2, "bath_room_count": 1, "kitchen_count": 1, "living_room_count": 1, "surface": 80, "rent_price": 300000, "price": 300000, "base_price_type": "per_month"},
    {"label": "Magasin — HLM Grand-Yoff", "type": "MAGASIN", "status": "for_rent", "rent_type": "RENT_EMPTY", "usage": "commercial", "country": "SN", "city": "Dakar", "zone": "Grand-Yoff",
        "bed_room_count": 0, "bath_room_count": 0, "kitchen_count": 0, "living_room_count": 0, "surface": 45, "rent_price": 200000, "price": 200000, "base_price_type": "per_month"},
    {"label": "Appartement F4 — Cité Keur Gorgui", "type": "F4", "status": "for_rent", "rent_type": "RENT_EMPTY", "usage": "residential", "country": "SN", "city": "Dakar", "zone": "Keur Gorgui",
        "bed_room_count": 3, "bath_room_count": 2, "kitchen_count": 1, "living_room_count": 1, "surface": 110, "rent_price": 600000, "price": 600000, "base_price_type": "per_month"},
    {"label": "Villa avec jardin — Hann Maristes", "type": "VILLA", "status": "for_sale", "rent_type": "SALE", "usage": "residential", "country": "SN", "city": "Dakar",
        "zone": "Hann Maristes", "bed_room_count": 4, "bath_room_count": 3, "kitchen_count": 1, "living_room_count": 2, "surface": 350, "sale_price": 175000000, "price": 175000000},
    {"label": "Studio — Ouest Foire", "type": "F2", "status": "for_rent", "rent_type": "RENT_FURNISHED", "usage": "residential", "country": "SN", "city": "Dakar", "zone": "Ouest Foire",
        "bed_room_count": 1, "bath_room_count": 1, "kitchen_count": 1, "living_room_count": 0, "surface": 30, "rent_price": 200000, "price": 200000, "base_price_type": "per_month"},
    {"label": "Appartement F5 — Sicap Baobab", "type": "F5", "status": "sold", "rent_type": "SALE", "usage": "residential", "country": "SN", "city": "Dakar",
        "zone": "Sicap Baobab", "bed_room_count": 4, "bath_room_count": 2, "kitchen_count": 1, "living_room_count": 2, "surface": 150, "sale_price": 85000000, "price": 85000000},
    {"label": "Villa R+2 — Dakar Yoff", "type": "VILLA", "status": "under_construction", "rent_type": "SALE", "usage": "residential", "country": "SN", "city": "Dakar",
        "zone": "Yoff", "bed_room_count": 8, "bath_room_count": 6, "kitchen_count": 2, "living_room_count": 3, "surface": 600, "sale_price": 650000000, "price": 650000000},
    {"label": "Appartement F3 — Ratoma Conakry", "type": "F3", "status": "for_rent", "rent_type": "RENT_FURNISHED", "usage": "residential", "country": "GN", "city": "Conakry", "zone": "Kipé",
        "bed_room_count": 2, "bath_room_count": 1, "kitchen_count": 1, "living_room_count": 1, "surface": 70, "rent_price": 3500000, "price": 3500000, "base_price_type": "per_month"},
]

# Currency by country
CURRENCY_MAP = {"SN": "XOF", "CI": "XOF", "GN": "GNF"}

# GPS coordinates per zone (approximate)
COORDS = {
    "Almadies": (14.7450, -17.5130), "Ngor": (14.7520, -17.5180), "Mermoz": (14.7170, -17.4800),
    "Liberté 6": (14.7170, -17.4620), "Fann": (14.7110, -17.4710), "Plateau": (14.6700, -17.4330),
    "Médina": (14.6730, -17.4430), "Point E": (14.6960, -17.4640), "Diamniadio": (14.7500, -17.1700),
    "Rufisque": (14.7160, -17.2680), "Lac Rose": (14.8400, -17.2330), "Mamelles": (14.7290, -17.5060),
    "Ouakam": (14.7250, -17.4930), "Sacré-Cœur": (14.7210, -17.4700), "Corniche": (14.7050, -17.4860),
    "Yoff": (14.7550, -17.4850), "Grand-Yoff": (14.7350, -17.4500), "Keur Gorgui": (14.7180, -17.4650),
    "Hann Maristes": (14.7280, -17.4200), "Ouest Foire": (14.7400, -17.4750),
    "Sicap Baobab": (14.7070, -17.4520), "Saly": (14.4480, -17.0170),
    "Île": (16.0230, -16.5020),
    "Cocody Riviera": (5.3580, -3.9720), "Cocody Angré": (5.3690, -3.9600),
    "Marcory": (5.3090, -3.9820), "Bingerville": (5.3550, -3.8910), "Assinie": (5.1570, -3.4730),
    "Kaloum": (9.5090, -13.7120), "Kipé": (9.5760, -13.6310), "Lambanyi": (9.5950, -13.5980),
}

# Placeholder images by property type
IMAGE_SEEDS = {
    "F2": [101, 102, 103, 104, 105],
    "F3": [111, 112, 113, 114, 115, 116],
    "F4": [121, 122, 123, 124, 125, 126],
    "F5": [131, 132, 133, 134, 135],
    "DUPLEX": [141, 142, 143, 144, 145, 146],
    "VILLA": [151, 152, 153, 154, 155, 156, 157],
    "OFFICE": [161, 162, 163, 164, 165],
    "MAGASIN": [171, 172, 173, 174],
    "LAND": [181, 182, 183],
    "PARKING": [191, 192],
}


async def seed_agencies(session: AsyncSession) -> list[Agency]:
    """Create 5 agencies."""
    agencies = []
    for data in AGENCIES:
        agency = Agency(**data)
        session.add(agency)
        agencies.append(agency)
    await session.flush()
    print(f"  ✓ {len(agencies)} agencies created")
    return agencies


async def seed_agents(session: AsyncSession, agencies: list[Agency], users: list[User]) -> list[Agent]:
    """Create 1 agent per user, distributed across agencies."""
    agents = []
    for i, user in enumerate(users):
        agency = agencies[i % len(agencies)]
        slug = f"{user.first_name.lower()}-{user.last_name.lower()}"
        agent = Agent(
            user_id=user.id,
            agency_id=agency.id,
            slug=slug,
        )
        session.add(agent)
        agents.append(agent)
    await session.flush()
    print(f"  ✓ {len(agents)} agents created")
    return agents


async def seed_properties(session: AsyncSession, agencies: list[Agency]) -> list[Property]:
    """Create 40 properties with realistic data."""
    properties = []
    code_counter = 1

    for tmpl in PROPERTY_TEMPLATES:
        # Match agency by country
        country = tmpl["country"]
        matching = [a for a in agencies if a.country == country]
        agency = random.choice(
            matching) if matching else random.choice(agencies)

        coords = COORDS.get(tmpl.get("zone"), (None, None))
        currency = CURRENCY_MAP.get(country, "XOF")

        prop = Property(
            agency_id=agency.id,
            label=tmpl["label"],
            code=f"KAY-{code_counter:04d}",
            status=tmpl["status"],
            type=tmpl["type"],
            rent_type=tmpl.get("rent_type"),
            usage=tmpl.get("usage"),
            rental_period=tmpl.get(
                "rental_period", "monthly" if "rent" in tmpl.get("status", "") else None),
            managed_by="agency",
            base_price_type=tmpl.get("base_price_type"),
            country=country,
            city=tmpl.get("city"),
            zone=tmpl.get("zone"),
            street=f"Rue {random.randint(1, 50)}",
            address=f"{tmpl.get('zone', '')}, {tmpl.get('city', '')}",
            bed_room_count=tmpl.get("bed_room_count", 0),
            bath_room_count=tmpl.get("bath_room_count", 0),
            kitchen_count=tmpl.get("kitchen_count", 0),
            living_room_count=tmpl.get("living_room_count", 0),
            surface=Decimal(str(tmpl.get("surface", 0))),
            lat=Decimal(str(coords[0])) if coords[0] else None,
            lng=Decimal(str(coords[1])) if coords[1] else None,
            build_year=str(random.randint(2005, 2024)
                           ) if tmpl["type"] != "LAND" else None,
            currency=currency,
            price=Decimal(str(tmpl.get("price", 0))
                          ) if tmpl.get("price") else None,
            sale_price=Decimal(str(tmpl.get("sale_price", 0))
                               ) if tmpl.get("sale_price") else None,
            rent_price=Decimal(str(tmpl.get("rent_price", 0))
                               ) if tmpl.get("rent_price") else None,
            base_price=Decimal(str(tmpl.get("price", 0))
                               ) if tmpl.get("price") else None,
            commission_rate=Decimal(str(random.choice([5, 8, 10]))),
            deposit_rate=Decimal(str(random.choice([100, 200]))) if tmpl.get(
                "rent_price") else None,
            vat_rate=Decimal("18") if country == "SN" else Decimal("18"),
            is_exposed=tmpl["status"] in ("for_sale", "for_rent", "free"),
            is_saleable=tmpl["status"] in ("for_sale", "free"),
            is_hidden=False,
            is_managed=True,
            is_featured=random.random() < 0.25,
            archived=tmpl["status"] in ("sold",),
            description=_generate_description(tmpl),
        )
        session.add(prop)
        properties.append(prop)
        code_counter += 1

    await session.flush()
    print(f"  ✓ {len(properties)} properties created")
    return properties


def _generate_description(tmpl: dict) -> str:
    """Generate a realistic French property description."""
    ptype = tmpl["type"]
    zone = tmpl.get("zone", "")
    surface = tmpl.get("surface", 0)
    beds = tmpl.get("bed_room_count", 0)
    baths = tmpl.get("bath_room_count", 0)

    if ptype == "LAND":
        return (
            f"Terrain de {surface}m² situé à {zone}. "
            f"Parcelle viabilisée avec accès route bitumée. "
            f"Titre foncier disponible. Idéal pour construction résidentielle ou investissement."
        )
    if ptype in ("OFFICE", "MAGASIN"):
        return (
            f"Espace professionnel de {surface}m² à {zone}. "
            f"Bien situé, accès facile, parking à proximité. "
            f"Idéal pour bureau, commerce ou activité libérale."
        )
    if ptype == "PARKING":
        return f"Place de parking sécurisée au cœur du {zone}. Gardiennage 24h/24."

    return (
        f"Magnifique {tmpl['label'].split('—')[0].strip().lower()} de {surface}m² "
        f"situé à {zone}. "
        f"{'Comprend' if beds else 'Dispose de'} {beds} chambre{'s' if beds > 1 else ''}, "
        f"{baths} salle{'s' if baths > 1 else ''} de bain. "
        f"Finitions de qualité, lumineux et bien ventilé. "
        f"Quartier calme et résidentiel avec toutes commodités à proximité."
    )


async def seed_property_images(session: AsyncSession, properties: list[Property]) -> int:
    """Create 3-5 placeholder images per property using picsum.photos."""
    total = 0
    for prop in properties:
        ptype = prop.type or "F3"
        seeds = IMAGE_SEEDS.get(ptype, [200, 201, 202, 203])
        min_seed = min(5, len(seeds))
        num_images = random.randint(3, min_seed if min_seed > 3 else 5)

        try:
            chosen = random.sample(seeds, num_images)
        except ValueError:
            chosen = seeds

        # First image becomes cover
        prop.image_url = f"https://picsum.photos/seed/{chosen[0]}/800/600"

        for seed_id in chosen:
            img = PropertyImage(
                property_id=prop.id,
                url=f"https://picsum.photos/seed/{seed_id}/800/600",
            )
            session.add(img)
            total += 1

    await session.flush()
    print(f"  ✓ {total} property images created")
    return total


async def seed_properties_data() -> None:
    """Main property seeder — creates agencies, agents, properties, and images."""
    print("\n🏗️  Seeding agencies, properties & images...")
    try:
        async with get_async_session_context() as session:
            # Check if data already exists
            existing = await session.execute(select(Agency.id).limit(1))
            if existing.scalar_one_or_none():
                print("  ℹ Agency/property data already exists, skipping")
                return

            users_result = await session.execute(select(User).limit(5))
            users = users_result.scalars().all()
            if not users:
                print("  ⚠ No users found — run base seed first")
                return

            agencies = await seed_agencies(session)
            await seed_agents(session, agencies, users)
            properties = await seed_properties(session, agencies)
            await seed_property_images(session, properties)

            await session.commit()
            print("✅ Agencies, properties & images seeded successfully!\n")

    except sqlalchemy.exc.IntegrityError as e:
        print(f"  ⚠ Data already exists or integrity error: {e}")
    except Exception as e:
        print(f"  ❌ Error seeding property data: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(seed_properties_data())
