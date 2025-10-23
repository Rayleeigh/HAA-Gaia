from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from enum import Enum


class ProviderType(str, Enum):
    """Supported provider types"""
    PROXMOX = "proxmox"
    VIRTUALBOX = "virtualbox"
    VMWARE = "vmware"
    WSL = "wsl"


class ProviderInfo(BaseModel):
    """Provider information"""
    name: str
    type: ProviderType
    display_name: str
    description: str
    version: Optional[str] = None
    enabled: bool = True
    requires_config: bool = True


class ProviderStatus(BaseModel):
    """Provider status"""
    name: str
    available: bool
    configured: bool
    version: Optional[str] = None
    message: Optional[str] = None
    details: Dict[str, Any] = {}
