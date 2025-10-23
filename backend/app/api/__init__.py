from fastapi import APIRouter
from app.api.endpoints import vms, templates, vagrantfiles, providers

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(vms.router, prefix="/vms", tags=["Virtual Machines"])
api_router.include_router(templates.router, prefix="/templates", tags=["Templates"])
api_router.include_router(vagrantfiles.router, prefix="/vagrantfiles", tags=["Vagrantfiles"])
api_router.include_router(providers.router, prefix="/providers", tags=["Providers"])
