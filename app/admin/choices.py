from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request


# module-level caches — populated once at startup via warm_choices_cache
_country_choices:            list[tuple[str, str]] = []
_city_choices:               list[tuple[str, str]] = []
_zone_choices:               list[tuple[str, str]] = []
_user_choices:               list[tuple[str, str]] = []
_agency_choices:             list[tuple[str, str]] = []
_property_type_choices:      list[tuple[str, str]] = []
_property_rent_type_choices: list[tuple[str, str]] = []
_city_id_choices:            list[tuple[str, str]] = []
_building_choices:           list[tuple[str, str]] = []
_property_choices:           list[tuple[str, str]] = []


async def warm_choices_cache(session: AsyncSession) -> None:
    global _country_choices, _city_choices, _zone_choices, _user_choices, _agency_choices
    global _property_type_choices, _property_rent_type_choices
    global _city_id_choices, _building_choices, _property_choices

    async def fetch(sql: str) -> list:
        return (await session.execute(text(sql))).fetchall()

    _country_choices = [
        (r[0], f"{r[1]} ({r[0]})" if r[1] else r[0])
        for r in await fetch(
            "SELECT code, name FROM country WHERE is_active = true ORDER BY name"
        )
    ]

    _city_choices = [
        (r[0], f"{r[1]} ({r[0]})" if r[1] else r[0])
        for r in await fetch(
            "SELECT code, name FROM city ORDER BY name"
        )
    ]

    _zone_choices = [
        (r[0], f"{r[1]} ({r[2]})" if r[2] else r[1])
        for r in await fetch(
            "SELECT name, name, city FROM area WHERE is_active = true ORDER BY city, name"
        )
    ]

    _user_choices = [
        (r[0], r[1])
        for r in await fetch(
            "SELECT id::text, first_name || ' ' || last_name || ' (' || email || ')'"
            " FROM \"user\" WHERE is_active = true ORDER BY first_name"
        )
    ]

    _agency_choices = [
        (r[0], r[1])
        for r in await fetch(
            "SELECT id::text, name || ' (' || country || ')'"
            " FROM agency WHERE is_active = true ORDER BY name"
        )
    ]

    _property_type_choices = [
        (r[0], r[1])
        for r in await fetch(
            "SELECT code, label FROM property_type WHERE is_active = true ORDER BY label"
        )
    ]

    _property_rent_type_choices = [
        (r[0], r[1])
        for r in await fetch(
            "SELECT code, label FROM property_rent_type WHERE is_active = true ORDER BY label"
        )
    ]

    _city_id_choices = [
        (r[0], r[1])
        for r in await fetch(
            "SELECT id::text, name || ' (' || code || ')'"
            " FROM city ORDER BY name"
        )
    ]

    _building_choices = [
        (r[0], r[1])
        for r in await fetch(
            "SELECT id::text, name FROM building ORDER BY name"
        )
    ]

    _property_choices = [
        (r[0], r[1])
        for r in await fetch(
            "SELECT id::text, COALESCE(label, code, id::text)"
            " FROM property_property ORDER BY label"
        )
    ]



def load_country_choices(request: Request) -> list[tuple[str, str]]:
    return _country_choices


def load_city_choices(request: Request) -> list[tuple[str, str]]:
    return _city_choices


def load_zone_choices(request: Request) -> list[tuple[str, str]]:
    return _zone_choices


def load_user_choices(request: Request) -> list[tuple[str, str]]:
    return _user_choices


def load_agency_choices(request: Request) -> list[tuple[str, str]]:
    return _agency_choices


def load_property_type_choices(request: Request) -> list[tuple[str, str]]:
    return _property_type_choices


def load_property_rent_type_choices(request: Request) -> list[tuple[str, str]]:
    return _property_rent_type_choices


def load_city_id_choices(request: Request) -> list[tuple[str, str]]:
    return _city_id_choices


def load_building_choices(request: Request) -> list[tuple[str, str]]:
    return _building_choices


def load_property_choices(request: Request) -> list[tuple[str, str]]:
    return _property_choices
