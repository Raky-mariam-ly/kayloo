# Copilot Instructions — Kayloo SiteWeb

## Build & Run

```bash
# Build and start (Docker required)
docker compose build
docker compose up -d

# Run Alembic migrations
docker exec web alembic upgrade head

# Create a new migration after model changes
docker exec web alembic revision --autogenerate -m "Describe change"

# View application logs
docker logs web -f
```

The app runs at `http://localhost:8000`. Admin panel is at `/admin` (superuser required).

## Architecture

FastAPI application with an async PostgreSQL backend (`asyncpg`), server-rendered public site (Jinja2), and a `starlette-admin` back-office. All application code lives under `app/`.

### Layered pattern

Each domain entity follows a strict 4-layer structure with 1:1 file mapping:

```
models/{entity}.py        → SQLAlchemy model (table definition)
repositories/{entity}.py  → Data access (extends BaseRepository)
services/{entity}.py      → Business logic (extends BaseService, delegates to repository)
admin/{entity}.py         → Admin CRUD view (extends AdminModelView)
```

**Dependency wiring in admin views** is manual, instantiated per method call:

```python
service = CountryService(CountryRepository(request.state.session))
```

### Key modules

- **`core/auth.py`** — Houses the shared SQLAlchemy `Base = declarative_base()` that all models import. Also configures fastapi-users (cookie-based JWT) and the `FastapiUsersAuthProvider` bridge for starlette-admin.
- **`core/db.py`** — Async engine + `get_db()` dependency (auto-commit/rollback).
- **`core/config.py`** — `pydantic-settings` with `.env` support, cached via `@lru_cache`.
- **`admin/admin.py`** — Registers all admin views using `DropDown` groupings.
- **`admin/base.py`** — `AdminModelView` base class with pagination defaults, export config, and custom fields (`ImageUploadField`, `SectionField`, `UUIDEnumField`).
- **`public/router.py`** — Jinja2-rendered HTML pages (currently uses static test data).
- **`seed.py`** — Runs at startup via `lifespan`; seeds users, property types, rent types, countries.

## Conventions

### Models

- All models inherit from `Base` (imported from `core.auth`, not a separate `db/base` module).
- **UUID primary keys**: `Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)`.
- **Audit fields** on every model: `created_at`, `updated_at` (auto-managed), `created_by`, `updated_by` (FK to `user.email`).
- Audit population uses **SQLAlchemy `before_insert`/`before_update` events** that read a `_current_user_id` attribute set on the instance before save.
- Table names are **singular snake_case** (e.g., `country`, `agency`, `property_property`).
- Monetary/rate fields use `Numeric(21, 6)`.

### Admin views

- Extend `AdminModelView` from `admin/base.py`.
- Declare explicit `fields` list with starlette-admin field types and French labels.
- Override CRUD methods (`create`, `edit`, `find_all`, `find_by_pk`, etc.) — each instantiates its own service/repository from `request.state.session`.
- Implement `validate()` for form validation (raises `FormValidationError`).
- Exclude audit fields from create/edit forms via `exclude_fields_from_create`/`exclude_fields_from_edit`.
- Set `_current_user_id` on entity before save for audit tracking.

### Repositories

- Extend `BaseRepository[T]` which provides generic CRUD + dynamic text search across all `String`/`Text` columns.
- Add entity-specific query methods (e.g., `get_by_code()`).

### Migrations

- After adding/changing a model, import it in `migrations/env.py` so Alembic autogenerate detects it.
- All migrations run inside Docker: `docker exec web alembic ...`.

### General

- The project uses **French** for UI labels, admin locale, and commit messages in README.
- File uploads go to `static/uploads/` with UUID-based filenames.
- The `api/v1/` directory exists but has no routes yet — the app currently serves only the public HTML site and admin panel.
