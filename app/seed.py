import logging
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from core.auth import create_user, get_async_session_context

from models.country import Country
from models.property_rent_type import PropertyRentType
from models.property_type import PropertyType


async def populate_users() -> None:
    users = [
        {
            "email": "szakou@groupesepro.com",
            "password": "p@55w0rd",
            "is_superuser": True,
            "first_name": "Seydou",
            "last_name": "Zakou",
            "phone_number": "+221 766001239",
            "gender": "M"
        },
        {
            "email": "emniang@groupesepro.com",
            "password": "p@55w0rd",
            "is_superuser": True,
            "first_name": "Elhadji Maodo",
            "last_name": "Niang",
            "phone_number": "+221 766001240",
            "gender": "M"
        },
        {
            "email": "hthiam@groupesepro.com",
            "password": "p@55w0rd",
            "is_superuser": True,
            "first_name": "Haby",
            "last_name": "Thiam",
            "phone_number": "+221 766001241",
            "gender": "F"
        },
        {
            "email": "rly@groupesepro.com",
            "password": "p@55w0rd",
            "is_superuser": True,
            "first_name": "Raky",
            "last_name": "Ly",
            "phone_number": "+221 766001242",
            "gender": "F"
        },
        {
            "email": "psba@groupesepro.com",
            "password": "p@55w0rd",
            "is_superuser": True,
            "first_name": "Pape Samba",
            "last_name": "BA",
            "phone_number": "+221 766001243",
            "gender": "M"
        }
    ]
    for user in users:
        try:
            await create_user(**user)
        except Exception as e:
            logger.warning("populate_users: skipped %s — %s", user["email"], e)


async def polulate_property_types() -> None:
    property_types = [
        {"code": "F2", "label": "Studio", "is_active": True},
        {"code": "F3", "label": "Appartement F3", "is_active": True},
        {"code": "F4", "label": "Appartement F4", "is_active": True},
        {"code": "F5", "label": "Appartement F5", "is_active": True},
        {"code": "DUPLEX", "label": "Duplex", "is_active": True},
        {"code": "VILLA", "label": "Villa", "is_active": True},
        {"code": "OFFICE", "label": "Bureau", "is_active": True},
        {"code": "MAGASIN", "label": "Magasin", "is_active": True},
        {"code": "LAND", "label": "Terrain", "is_active": True},
        {"code": "PARKING", "label": "Parking", "is_active": True},
    ]
    try:
        async with get_async_session_context() as session:
            for pt in property_types:
                session.add(PropertyType(**pt))
            await session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        print(f"Table already populated: {e}")


async def populate_countries() -> None:
    countries = [
        {"code": "SN", "name": "Senegal", "is_active": True},
        {"code": "CI", "name": "Côte d'Ivoire", "is_active": True},
        {"code": "GN", "name": "Guinée", "is_active": True},
        # {"code": "BF", "name": "Burkina Faso", "is_active": True},
        # {"code": "GM", "name": "Gambia", "is_active": True},
        # {"code": "BJ", "name": "Benin", "is_active": True},
    ]
    try:
        async with get_async_session_context() as session:
            for country in countries:
                session.add(Country(**country))
            await session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        print(f"Table already populated: {e}")


async def polulate_property_rent_types() -> None:
    property_rent_types = [
        {"code": "RENT_EMPTY", "label": "Location Vide", "is_active": True},
        {"code": "RENT_FURNISHED", "label": "Location Meublée", "is_active": True},
        {"code": "SALE", "label": "Vente", "is_active": True},
        {"code": "LEASE_AGRO", "label": "Location Agricole", "is_active": True},
    ]
    try:
        async with get_async_session_context() as session:
            for prt in property_rent_types:
                session.add(PropertyRentType(**prt))
            await session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        print(f"Table already populated: {e}")


async def seed_database() -> None:
    await populate_users()
    await polulate_property_types()
    await polulate_property_rent_types()
    await populate_countries()
    # Agencies, agents, properties, images
    from seed_properties import seed_properties_data
    await seed_properties_data()
    try:
        from seed_crm import seed_crm_data
        await seed_crm_data()
    except Exception:
        import logging
        logging.getLogger(__name__).warning("seed_crm ignoré : tables CRM absentes ou erreur", exc_info=True)
