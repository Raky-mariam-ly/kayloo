from sqlalchemy import engine
from starlette_admin import I18nConfig
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.i18n import SUPPORTED_LOCALES
from starlette_admin.contrib.sqla import Admin

from core.config import get_settings
from core.auth import FastapiUsersAuthProvider, User
from core.db import engine

from models.country import Country
from models.property_rent_type import PropertyRentType
from models.property_type import PropertyType

from admin.country import CountryView
from admin.property_rent_type import PropertyRentTypeView
from admin.property_type import PropertyTypeView
from admin.user import UserView


settings = get_settings()

# Create admin
admin = Admin(engine,
              i18n_config=I18nConfig(
                  default_locale="fr", language_switcher=SUPPORTED_LOCALES),
              base_url="/admin",
              statics_dir="static",
              templates_dir="templates/admin",
              logo_url="/static/logo.svg",
              login_logo_url="/static/logo.svg",
              auth_provider=FastapiUsersAuthProvider(
                  allow_paths=["static/logo.svg"]),
              middlewares=[Middleware(
                  SessionMiddleware, secret_key=settings.secret)],
              )

admin.add_view(UserView(User, icon="fa fa-users", label="Users"))
admin.add_view(PropertyTypeView(
    PropertyType, icon="fa fa-cogs", label="Property Types"))
admin.add_view(PropertyRentTypeView(
    PropertyRentType, icon="fa fa-cogs", label="Property Rent Types"))
admin.add_view(CountryView(Country, icon="fa fa-flag", label="Countries"))
