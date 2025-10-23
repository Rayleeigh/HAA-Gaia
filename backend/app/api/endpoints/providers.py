from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.services.providers.base import ProviderRegistry
from app.schemas.provider import ProviderInfo, ProviderStatus

# Import all providers to ensure they register themselves
import app.services.providers

router = APIRouter()


@router.get("/", response_model=List[ProviderInfo])
async def list_providers():
    """List all available providers"""
    registry = ProviderRegistry()
    providers = registry.list_providers()
    return providers


@router.get("/{provider_name}", response_model=ProviderInfo)
async def get_provider_info(provider_name: str):
    """Get information about a specific provider"""
    registry = ProviderRegistry()
    provider_info = registry.get_provider_info(provider_name)
    if not provider_info:
        raise HTTPException(status_code=404, detail=f"Provider '{provider_name}' not found")
    return provider_info


@router.get("/{provider_name}/status", response_model=ProviderStatus)
async def get_provider_status(provider_name: str):
    """Check if a provider is available and configured"""
    registry = ProviderRegistry()
    provider = registry.get_provider(provider_name)
    if not provider:
        raise HTTPException(status_code=404, detail=f"Provider '{provider_name}' not found")

    status = await provider.check_status()
    return status


@router.get("/{provider_name}/capabilities")
async def get_provider_capabilities(provider_name: str) -> Dict[str, Any]:
    """Get provider capabilities and supported features"""
    registry = ProviderRegistry()
    provider = registry.get_provider(provider_name)
    if not provider:
        raise HTTPException(status_code=404, detail=f"Provider '{provider_name}' not found")

    capabilities = provider.get_capabilities()
    return capabilities
