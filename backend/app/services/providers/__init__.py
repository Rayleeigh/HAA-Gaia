# Import all providers to trigger their registration
from app.services.providers.proxmox import ProxmoxProvider
from app.services.providers.virtualbox import VirtualBoxProvider
from app.services.providers.hyperv import HyperVProvider
from app.services.providers.wsl import WSLProvider

# Export for convenience
__all__ = [
    'ProxmoxProvider',
    'VirtualBoxProvider',
    'HyperVProvider',
    'WSLProvider',
]
