from starlette_admin import ExportType
from starlette_admin.contrib.sqla import ModelView


AVAILABLE_USER_ROLES = [
    ("superadmin", "Super Admin"),
    ("admin", "Admin"),
    ("manager", "Manager"),
    ("viewer", "Viewer"),
]

GENDER_TYPES = [
    ("M", "Male"),
    ("F", "Female"),
]


class AdminModelView(ModelView):
    page_size = 25
    page_size_options = [10, 25, 50, 100]
    export_types = [ExportType.EXCEL, ExportType.CSV]
