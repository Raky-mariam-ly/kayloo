from fastapi import APIRouter

from api.v1.country import router as country_router
from api.v1.city import router as city_router
from api.v1.area import router as area_router
from api.v1.agency import router as agency_router
from api.v1.agent import router as agent_router
from api.v1.building import router as building_router
from api.v1.partner import router as partner_router
from api.v1.property_type import router as property_type_router
from api.v1.property_rent_type import router as property_rent_type_router
from api.v1.property import router as property_router
from api.v1.property_image import router as property_image_router
from api.v1.property_view import router as property_view_router
from api.v1.property_review import router as property_review_router
from api.v1.property_review import admin_router as review_admin_router
from api.v1.auth import router as auth_router

router = APIRouter(prefix="/api/v1")
router.include_router(country_router)
router.include_router(city_router)
router.include_router(area_router)
router.include_router(agency_router)
router.include_router(agent_router)
router.include_router(building_router)
router.include_router(partner_router)
router.include_router(property_type_router)
router.include_router(property_rent_type_router)
router.include_router(property_router)
router.include_router(property_image_router)
router.include_router(property_view_router)
router.include_router(property_review_router)
router.include_router(review_admin_router)