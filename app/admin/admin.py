from starlette_admin import I18nConfig, DropDown
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
from models.city import City
from models.area import Area
from models.agency import Agency
from models.agent import Agent
from models.partner import Partner
from models.property import Property
from models.building import Building
from models.property_image import PropertyImage  # noqa: F401 — requis pour les relations SQLAlchemy
from models.property_gallery import PropertyGallery  # noqa: F401 — requis pour les relations SQLAlchemy

from admin.country import CountryView
from admin.property_rent_type import PropertyRentTypeView
from admin.property_type import PropertyTypeView
from admin.user import UserView
from admin.city import CityView
from admin.area import AreaView
from admin.agency import AgencyView
from admin.agent import AgentView
from admin.partner import PartnerView
from admin.property import PropertyView
from admin.building import BuildingView
from admin.profile import ProfileView, ProfileUploadView, ProfileChangePasswordView, ProfileDeleteView, ProfileAgencyView
from admin.viewer import ViewerFavorisView, ViewerMessagesView
from admin.manager_views import (
    ManagerDashboardView, ManagerActivitesView, ManagerStatistiquesView,
    ManagerOffresView, ManagerProspectsView, ManagerDemandesView,
)


settings = get_settings()

# Create admin
admin = Admin(engine,
              title="Kayloo Admin",
              i18n_config=I18nConfig(
                  default_locale="fr", language_switcher=SUPPORTED_LOCALES),
              base_url="/admin",
              statics_dir="static",
              templates_dir="templates/admin",
              logo_url="/static/logo.svg?v=3",
              login_logo_url="/static/logo-login.svg",
              favicon_url="/static/logo.svg?v=3",
              auth_provider=FastapiUsersAuthProvider(
                  allow_paths=["static/logo.svg"]),
              middlewares=[Middleware(
                  SessionMiddleware, secret_key=settings.secret)],
              )

# ── Utilisateurs ──
admin.add_view(UserView(User, icon="fa fa-users", label="Utilisateurs"))

# ── Localisation ──
admin.add_view(DropDown(
    label="Localisation",
    icon="fa fa-globe",
    views=[
        CountryView(Country, icon="fa fa-flag", label="Pays"),
        CityView(City, icon="fa fa-city", label="Villes"),
        AreaView(Area, icon="fa fa-map-marker", label="Zones"),
    ]
))

# ── Professionnels ──
admin.add_view(DropDown(
    label="Professionnels",
    icon="fa fa-briefcase",
    views=[
        AgencyView(Agency, icon="fa fa-building", label="Agences"),
        AgentView(Agent, icon="fa fa-id-badge", label="Agents"),
        PartnerView(Partner, icon="fa fa-handshake", label="Partenaires"),
    ]
))

# ── Propriétés ──
admin.add_view(DropDown(
    label="Biens",
    icon="fa fa-home",
    views=[
        PropertyTypeView(PropertyType, icon="fa fa-cogs", label="Types de bien"),
        PropertyRentTypeView(PropertyRentType, icon="fa fa-cogs", label="Types de location"),
        BuildingView(Building, icon="fa fa-building-o", label="Immeubles"),
        PropertyView(Property, icon="fa fa-home", label="Biens"),
    ]
))

# ── Compte (profil — add_to_menu=False : rendu manuellement dans le sidebar) ──
admin.add_view(ProfileView())
admin.add_view(ProfileUploadView())
admin.add_view(ProfileChangePasswordView())
admin.add_view(ProfileDeleteView())
admin.add_view(ProfileAgencyView())
admin.add_view(ViewerFavorisView())
admin.add_view(ViewerMessagesView())

# ── Manager (agent) views ──
admin.add_view(ManagerDashboardView())
admin.add_view(ManagerActivitesView())
admin.add_view(ManagerStatistiquesView())
admin.add_view(ManagerOffresView())
admin.add_view(ManagerProspectsView())
admin.add_view(ManagerDemandesView())

