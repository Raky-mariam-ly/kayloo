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
from models.property_image import PropertyImage  # noqa: F401
from models.property_gallery import PropertyGallery  # noqa: F401

from models.contact import Contact
from models.lead import Lead
from models.activity import Activity
from models.task import Task
from models.notification import Notification
from models.conversation import Conversation

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
from admin.viewer import ViewerFavoritesView, ViewerMessagesView
from admin.manager_views import (
    ManagerDashboardView, ManagerActivitiesView, ManagerStatisticsView,
    ManagerOffersView, ManagerProspectsView, ManagerRequestsView,
)

from admin.contact import ContactView
from admin.lead import LeadView
from admin.activity import ActivityView
from admin.task import TaskView
from admin.notification import NotificationView
from admin.conversation import ConversationView
from admin.crm_dashboard import CrmDashboardView
from admin.lead_kanban import LeadKanbanView


settings = get_settings()

admin = Admin(engine,
              title="Kayloo Admin",
              i18n_config=I18nConfig(
                  default_locale="en", language_switcher=SUPPORTED_LOCALES),
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

admin.add_view(UserView(User, icon="fa fa-users", label="Users"))

admin.add_view(DropDown(
    label="Location",
    icon="fa fa-globe",
    views=[
        CountryView(Country, icon="fa fa-flag", label="Countries"),
        CityView(City, icon="fa fa-city", label="Cities"),
        AreaView(Area, icon="fa fa-map-marker", label="Areas"),
    ]
))

admin.add_view(DropDown(
    label="Professionals",
    icon="fa fa-briefcase",
    views=[
        AgencyView(Agency, icon="fa fa-building", label="Agencies"),
        AgentView(Agent, icon="fa fa-id-badge", label="Agents"),
        PartnerView(Partner, icon="fa fa-handshake", label="Partners"),
    ]
))

admin.add_view(DropDown(
    label="Properties",
    icon="fa fa-home",
    views=[
        PropertyTypeView(PropertyType, icon="fa fa-cogs", label="Property Types"),
        PropertyRentTypeView(PropertyRentType, icon="fa fa-cogs", label="Rental Types"),
        BuildingView(Building, icon="fa fa-building-o", label="Buildings"),
        PropertyView(Property, icon="fa fa-home", label="Properties"),
    ]
))

admin.add_view(ProfileView())
admin.add_view(ProfileUploadView())
admin.add_view(ProfileChangePasswordView())
admin.add_view(ProfileDeleteView())
admin.add_view(ProfileAgencyView())
admin.add_view(ViewerFavoritesView())
admin.add_view(ViewerMessagesView())

admin.add_view(ManagerDashboardView())
admin.add_view(ManagerActivitiesView())
admin.add_view(ManagerStatisticsView())
admin.add_view(ManagerOffersView())
admin.add_view(ManagerProspectsView())
admin.add_view(ManagerRequestsView())

admin.add_view(DropDown(
    label="CRM",
    icon="fa fa-handshake",
    views=[
        CrmDashboardView(),
        LeadKanbanView(),
        ContactView(Contact, icon="fa fa-address-book", label="Contacts"),
        LeadView(Lead, icon="fa fa-funnel-dollar", label="Leads"),
        ActivityView(Activity, icon="fa fa-history", label="Activities"),
        TaskView(Task, icon="fa fa-tasks", label="Tasks"),
        ConversationView(Conversation, icon="fa fa-comments", label="Conversations"),
        NotificationView(Notification, icon="fa fa-bell", label="Notifications"),
    ]
))
