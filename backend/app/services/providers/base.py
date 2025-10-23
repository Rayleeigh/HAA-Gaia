from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from app.schemas.provider import ProviderInfo, ProviderStatus, ProviderType


class BaseProvider(ABC):
    """
    Base class for all virtualization providers.

    Each provider must implement these core methods to support
    the unified orchestration interface.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name"""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable provider name"""
        pass

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Provider type enum"""
        pass

    @abstractmethod
    async def check_status(self) -> ProviderStatus:
        """
        Check if provider is available and properly configured.
        Returns ProviderStatus with availability information.
        """
        pass

    @abstractmethod
    async def create_vm(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new virtual machine.

        Args:
            config: VM configuration dictionary

        Returns:
            Dict containing VM details including provider-specific ID
        """
        pass

    @abstractmethod
    async def start_vm(self, vm_id: str) -> bool:
        """Start a virtual machine"""
        pass

    @abstractmethod
    async def stop_vm(self, vm_id: str) -> bool:
        """Stop a virtual machine"""
        pass

    @abstractmethod
    async def delete_vm(self, vm_id: str) -> bool:
        """Delete/destroy a virtual machine"""
        pass

    @abstractmethod
    async def get_vm_status(self, vm_id: str) -> Dict[str, Any]:
        """
        Get current status of a virtual machine.

        Returns:
            Dict with status information (state, IP, resources, etc.)
        """
        pass

    @abstractmethod
    async def list_vms(self) -> List[Dict[str, Any]]:
        """List all VMs managed by this provider"""
        pass

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get provider capabilities.
        Override in subclass to provide specific capabilities.
        """
        return {
            "supports_snapshots": False,
            "supports_cloning": False,
            "supports_live_migration": False,
            "supports_networking": True,
            "supports_storage": True,
            "supports_provisioning": True
        }

    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate VM configuration for this provider.

        Returns:
            Tuple of (is_valid, error_message)
        """
        return True, None


class ProviderRegistry:
    """
    Registry for all available providers.
    Implements plugin-like architecture for easy provider addition.
    """

    _providers: Dict[str, type[BaseProvider]] = {}

    @classmethod
    def register(cls, provider_class: type[BaseProvider]):
        """Register a provider class"""
        # Get an instance to access name property
        temp_instance = provider_class()
        cls._providers[temp_instance.name] = provider_class
        return provider_class

    @classmethod
    def get_provider(cls, name: str, config: Dict[str, Any] = None) -> Optional[BaseProvider]:
        """Get a provider instance by name"""
        provider_class = cls._providers.get(name)
        if provider_class:
            return provider_class(config)
        return None

    @classmethod
    def list_providers(cls) -> List[ProviderInfo]:
        """List all registered providers"""
        providers = []
        for provider_class in cls._providers.values():
            instance = provider_class()
            providers.append(ProviderInfo(
                name=instance.name,
                type=instance.provider_type,
                display_name=instance.display_name,
                description=instance.__doc__ or "",
                enabled=True,
                requires_config=True
            ))
        return providers

    @classmethod
    def get_provider_info(cls, name: str) -> Optional[ProviderInfo]:
        """Get information about a specific provider"""
        provider_class = cls._providers.get(name)
        if provider_class:
            instance = provider_class()
            return ProviderInfo(
                name=instance.name,
                type=instance.provider_type,
                display_name=instance.display_name,
                description=instance.__doc__ or "",
                enabled=True,
                requires_config=True
            )
        return None
