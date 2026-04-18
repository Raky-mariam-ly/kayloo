import os
import psycopg2
from starlette.requests import Request


def _get_sync_conn():
    db_url = os.environ.get("DATABASE_URL", "").replace("+asyncpg", "")
    return psycopg2.connect(db_url)


def load_country_choices(request: Request):
    conn = _get_sync_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT code, name FROM country WHERE is_active = true ORDER BY name"
            )
            rows = cur.fetchall()
        return [(r[0], f"{r[1]} ({r[0]})" if r[1] else r[0]) for r in rows]
    finally:
        conn.close()


def load_city_choices(request: Request):
    conn = _get_sync_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT code, name FROM city WHERE is_active = true ORDER BY name"
            )
            rows = cur.fetchall()
        return [(r[0], f"{r[1]} ({r[0]})" if r[1] else r[0]) for r in rows]
    finally:
        conn.close()


def load_user_choices(request: Request):
    conn = _get_sync_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id::text, first_name || ' ' || last_name || ' (' || email || ')' FROM \"user\" WHERE is_active = true ORDER BY first_name"
            )
            rows = cur.fetchall()
        return [(r[0], r[1]) for r in rows]
    finally:
        conn.close()


def load_agency_choices(request: Request):
    conn = _get_sync_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id::text, name || ' (' || country || ')' FROM agency WHERE is_active = true ORDER BY name"
            )
            rows = cur.fetchall()
        return [(r[0], r[1]) for r in rows]
    finally:
        conn.close()


def load_property_type_choices(request: Request):
    conn = _get_sync_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT code, label FROM property_type WHERE is_active = true ORDER BY label"
            )
            rows = cur.fetchall()
        return [(r[0], r[1]) for r in rows]
    finally:
        conn.close()


def load_property_rent_type_choices(request: Request):
    conn = _get_sync_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT code, label FROM property_rent_type WHERE is_active = true ORDER BY label"
            )
            rows = cur.fetchall()
        return [(r[0], r[1]) for r in rows]
    finally:
        conn.close()


def load_city_id_choices(request: Request):
    conn = _get_sync_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id::text, name || ' (' || code || ')' FROM city WHERE is_active = true ORDER BY name"
            )
            rows = cur.fetchall()
        return [(r[0], r[1]) for r in rows]
    finally:
        conn.close()


def load_building_choices(request: Request):
    conn = _get_sync_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id::text, name FROM building ORDER BY name"
            )
            rows = cur.fetchall()
        return [(r[0], r[1]) for r in rows]
    finally:
        conn.close()


def load_property_choices(request: Request):
    conn = _get_sync_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id::text, COALESCE(label, code, id::text) FROM property_property ORDER BY label"
            )
            rows = cur.fetchall()
        return [(r[0], r[1]) for r in rows]
    finally:
        conn.close()
