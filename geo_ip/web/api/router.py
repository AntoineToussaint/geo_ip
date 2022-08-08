from fastapi.routing import APIRouter

from geo_ip.web.api import geo_ip

api_router = APIRouter()
api_router.include_router(geo_ip.router)
