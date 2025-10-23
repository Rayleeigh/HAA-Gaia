from typing import Dict, Any, List, Optional
from proxmoxer import ProxmoxAPI
from proxmoxer.core import ResourceException
import asyncio

from app.services.providers.base import BaseProvider, ProviderRegistry
from app.schemas.provider import ProviderStatus, ProviderType
from app.core.config import settings


@ProviderRegistry.register
class ProxmoxProvider(BaseProvider):
    """
    Proxmox Virtual Environment provider.

    Supports creating and managing VMs on Proxmox VE clusters.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self._client: Optional[ProxmoxAPI] = None

    @property
    def name(self) -> str:
        return "proxmox"

    @property
    def display_name(self) -> str:
        return "Proxmox VE"

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.PROXMOX

    def _get_client(self) -> ProxmoxAPI:
        """Get or create Proxmox API client"""
        if self._client is None:
            host = self.config.get('host') or settings.PROXMOX_HOST
            user = self.config.get('user') or settings.PROXMOX_USER
            password = self.config.get('password') or settings.PROXMOX_PASSWORD
            verify_ssl = self.config.get('verify_ssl', settings.PROXMOX_VERIFY_SSL)

            if not host or not user or not password:
                raise ValueError("Proxmox connection details not configured")

            self._client = ProxmoxAPI(
                host,
                user=user,
                password=password,
                verify_ssl=verify_ssl
            )

        return self._client

    async def check_status(self) -> ProviderStatus:
        """Check if Proxmox is available and configured"""
        try:
            client = self._get_client()
            # Try to get cluster status
            version = await asyncio.to_thread(client.version.get)

            return ProviderStatus(
                name=self.name,
                available=True,
                configured=True,
                version=version.get('version'),
                message="Connected to Proxmox VE",
                details={"release": version.get('release')}
            )
        except ValueError as e:
            return ProviderStatus(
                name=self.name,
                available=False,
                configured=False,
                message=str(e)
            )
        except Exception as e:
            return ProviderStatus(
                name=self.name,
                available=False,
                configured=True,
                message=f"Connection failed: {str(e)}"
            )

    async def create_vm(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new VM in Proxmox"""
        client = self._get_client()

        # Extract configuration
        node = config.get('node') or config.get('provider_config', {}).get('node', 'pve')
        vm_name = config.get('name')
        vm_id = config.get('vmid') or await self._get_next_vmid(node)

        # Build VM configuration
        vm_config = {
            'vmid': vm_id,
            'name': vm_name,
            'cores': config.get('cpus', 2),
            'memory': config.get('memory', 2048),
            'net0': f"virtio,bridge={config.get('bridge', 'vmbr0')}",
        }

        # Add storage configuration
        storage = config.get('provider_config', {}).get('storage', 'local-lvm')
        disk_size = config.get('provider_config', {}).get('disk_size', '32G')
        vm_config['scsi0'] = f"{storage}:{disk_size}"

        # Add OS type if specified
        if 'ostype' in config.get('provider_config', {}):
            vm_config['ostype'] = config['provider_config']['ostype']

        # Create the VM
        result = await asyncio.to_thread(
            client.nodes(node).qemu.create,
            **vm_config
        )

        return {
            'provider_vm_id': str(vm_id),
            'node': node,
            'vmid': vm_id,
            'name': vm_name,
            'status': 'created'
        }

    async def start_vm(self, vm_id: str) -> bool:
        """Start a VM"""
        try:
            client = self._get_client()
            node, vmid = self._parse_vm_id(vm_id)

            await asyncio.to_thread(
                client.nodes(node).qemu(vmid).status.start.post
            )
            return True
        except Exception as e:
            print(f"Error starting VM: {e}")
            return False

    async def stop_vm(self, vm_id: str) -> bool:
        """Stop a VM"""
        try:
            client = self._get_client()
            node, vmid = self._parse_vm_id(vm_id)

            await asyncio.to_thread(
                client.nodes(node).qemu(vmid).status.shutdown.post
            )
            return True
        except Exception as e:
            print(f"Error stopping VM: {e}")
            return False

    async def delete_vm(self, vm_id: str) -> bool:
        """Delete a VM"""
        try:
            client = self._get_client()
            node, vmid = self._parse_vm_id(vm_id)

            # Stop VM first if running
            await self.stop_vm(vm_id)

            # Wait a bit for shutdown
            await asyncio.sleep(2)

            # Delete the VM
            await asyncio.to_thread(
                client.nodes(node).qemu(vmid).delete
            )
            return True
        except Exception as e:
            print(f"Error deleting VM: {e}")
            return False

    async def get_vm_status(self, vm_id: str) -> Dict[str, Any]:
        """Get VM status"""
        try:
            client = self._get_client()
            node, vmid = self._parse_vm_id(vm_id)

            status = await asyncio.to_thread(
                client.nodes(node).qemu(vmid).status.current.get
            )

            return {
                'state': self._map_proxmox_state(status.get('status')),
                'provider_state': status.get('status'),
                'cpu_usage': status.get('cpu'),
                'memory_usage': status.get('mem'),
                'uptime': status.get('uptime'),
                'name': status.get('name')
            }
        except Exception as e:
            return {
                'state': 'unknown',
                'error': str(e)
            }

    async def list_vms(self) -> List[Dict[str, Any]]:
        """List all VMs across all nodes"""
        try:
            client = self._get_client()
            nodes = await asyncio.to_thread(client.nodes.get)

            all_vms = []
            for node in nodes:
                node_name = node['node']
                vms = await asyncio.to_thread(
                    client.nodes(node_name).qemu.get
                )

                for vm in vms:
                    all_vms.append({
                        'provider_vm_id': f"{node_name}:{vm['vmid']}",
                        'vmid': vm['vmid'],
                        'name': vm['name'],
                        'status': vm['status'],
                        'node': node_name
                    })

            return all_vms
        except Exception as e:
            print(f"Error listing VMs: {e}")
            return []

    def get_capabilities(self) -> Dict[str, Any]:
        """Get Proxmox provider capabilities"""
        return {
            "supports_snapshots": True,
            "supports_cloning": True,
            "supports_live_migration": True,
            "supports_networking": True,
            "supports_storage": True,
            "supports_provisioning": True,
            "supports_ha": True,
            "supports_backup": True
        }

    def _parse_vm_id(self, vm_id: str) -> tuple[str, str]:
        """Parse VM ID in format 'node:vmid'"""
        if ':' in vm_id:
            node, vmid = vm_id.split(':', 1)
            return node, vmid
        else:
            # Default to first available node
            return 'pve', vm_id

    async def _get_next_vmid(self, node: str) -> int:
        """Get next available VM ID"""
        client = self._get_client()
        next_id = await asyncio.to_thread(client.cluster.nextid.get)
        return int(next_id)

    def _map_proxmox_state(self, proxmox_state: str) -> str:
        """Map Proxmox state to our standard states"""
        state_map = {
            'running': 'running',
            'stopped': 'stopped',
            'paused': 'suspended'
        }
        return state_map.get(proxmox_state, 'unknown')
