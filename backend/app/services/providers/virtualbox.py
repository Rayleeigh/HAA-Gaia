from typing import Dict, Any, List, Optional
import asyncio
import subprocess
import re
import json

from app.services.providers.base import BaseProvider, ProviderRegistry
from app.schemas.provider import ProviderStatus, ProviderType


@ProviderRegistry.register
class VirtualBoxProvider(BaseProvider):
    """
    VirtualBox provider.

    Supports creating and managing VMs using Oracle VirtualBox.
    Uses VBoxManage CLI for VM operations.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)

    @property
    def name(self) -> str:
        return "virtualbox"

    @property
    def display_name(self) -> str:
        return "VirtualBox"

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.VIRTUALBOX

    async def check_status(self) -> ProviderStatus:
        """Check if VirtualBox is installed and available"""
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                ["VBoxManage", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                version = result.stdout.strip()
                return ProviderStatus(
                    name=self.name,
                    available=True,
                    configured=True,
                    version=version,
                    message=f"VirtualBox {version} is available"
                )
            else:
                return ProviderStatus(
                    name=self.name,
                    available=False,
                    configured=False,
                    message="VirtualBox is not responding properly"
                )

        except FileNotFoundError:
            return ProviderStatus(
                name=self.name,
                available=False,
                configured=False,
                message="VirtualBox is not installed or not in PATH"
            )
        except Exception as e:
            return ProviderStatus(
                name=self.name,
                available=False,
                configured=False,
                message=f"Error checking VirtualBox: {str(e)}"
            )

    async def create_vm(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new VM in VirtualBox"""
        vm_name = config.get('name')
        cpus = config.get('cpus', 2)
        memory = config.get('memory', 2048)

        try:
            # Create VM
            await self._run_vboxmanage([
                "createvm",
                "--name", vm_name,
                "--ostype", config.get('ostype', 'Ubuntu_64'),
                "--register"
            ])

            # Configure VM
            await self._run_vboxmanage([
                "modifyvm", vm_name,
                "--memory", str(memory),
                "--cpus", str(cpus),
                "--vram", "128",
                "--nic1", "nat"
            ])

            # Create hard disk if specified
            disk_size = config.get('disk_size', 32768)  # MB
            disk_path = f"{vm_name}.vdi"

            await self._run_vboxmanage([
                "createhd",
                "--filename", disk_path,
                "--size", str(disk_size),
                "--format", "VDI"
            ])

            # Add SATA controller
            await self._run_vboxmanage([
                "storagectl", vm_name,
                "--name", "SATA Controller",
                "--add", "sata",
                "--controller", "IntelAhci"
            ])

            # Attach disk
            await self._run_vboxmanage([
                "storageattach", vm_name,
                "--storagectl", "SATA Controller",
                "--port", "0",
                "--device", "0",
                "--type", "hdd",
                "--medium", disk_path
            ])

            return {
                'provider_vm_id': vm_name,
                'name': vm_name,
                'status': 'created',
                'cpus': cpus,
                'memory': memory
            }

        except Exception as e:
            # Cleanup on failure
            try:
                await self._run_vboxmanage(["unregistervm", vm_name, "--delete"])
            except:
                pass
            raise Exception(f"Failed to create VM: {str(e)}")

    async def start_vm(self, vm_id: str) -> bool:
        """Start a VM"""
        try:
            await self._run_vboxmanage([
                "startvm", vm_id, "--type", "headless"
            ])
            return True
        except Exception as e:
            print(f"Error starting VM: {e}")
            return False

    async def stop_vm(self, vm_id: str) -> bool:
        """Stop a VM"""
        try:
            # Try graceful shutdown first
            await self._run_vboxmanage([
                "controlvm", vm_id, "acpipowerbutton"
            ])

            # Wait a bit for graceful shutdown
            await asyncio.sleep(5)

            # Check if still running, force power off if needed
            status = await self.get_vm_status(vm_id)
            if status.get('state') == 'running':
                await self._run_vboxmanage([
                    "controlvm", vm_id, "poweroff"
                ])

            return True
        except Exception as e:
            print(f"Error stopping VM: {e}")
            return False

    async def delete_vm(self, vm_id: str) -> bool:
        """Delete a VM"""
        try:
            # Stop VM if running
            await self.stop_vm(vm_id)

            # Wait for shutdown
            await asyncio.sleep(2)

            # Delete VM and all files
            await self._run_vboxmanage([
                "unregistervm", vm_id, "--delete"
            ])
            return True
        except Exception as e:
            print(f"Error deleting VM: {e}")
            return False

    async def get_vm_status(self, vm_id: str) -> Dict[str, Any]:
        """Get VM status"""
        try:
            # Get VM info
            result = await self._run_vboxmanage([
                "showvminfo", vm_id, "--machinereadable"
            ])

            # Parse the output
            info = {}
            for line in result.stdout.split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    info[key.strip()] = value.strip().strip('"')

            state = info.get('VMState', 'unknown')

            return {
                'state': self._map_vbox_state(state),
                'provider_state': state,
                'name': info.get('name', vm_id),
                'cpus': info.get('cpus'),
                'memory': info.get('memory')
            }
        except Exception as e:
            return {
                'state': 'unknown',
                'error': str(e)
            }

    async def list_vms(self) -> List[Dict[str, Any]]:
        """List all VMs"""
        try:
            result = await self._run_vboxmanage(["list", "vms"])

            vms = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    # Format: "name" {uuid}
                    match = re.match(r'"(.+)"\s+\{(.+)\}', line)
                    if match:
                        name = match.group(1)
                        uuid = match.group(2)

                        # Get status for each VM
                        status = await self.get_vm_status(name)

                        vms.append({
                            'provider_vm_id': name,
                            'name': name,
                            'uuid': uuid,
                            'status': status.get('state', 'unknown')
                        })

            return vms
        except Exception as e:
            print(f"Error listing VMs: {e}")
            return []

    def get_capabilities(self) -> Dict[str, Any]:
        """Get VirtualBox provider capabilities"""
        return {
            "supports_snapshots": True,
            "supports_cloning": True,
            "supports_live_migration": False,
            "supports_networking": True,
            "supports_storage": True,
            "supports_provisioning": True,
            "supports_gui": True,
            "supports_headless": True
        }

    async def _run_vboxmanage(self, args: List[str]) -> subprocess.CompletedProcess:
        """Run VBoxManage command"""
        result = await asyncio.to_thread(
            subprocess.run,
            ["VBoxManage"] + args,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            raise Exception(f"VBoxManage error: {result.stderr}")

        return result

    def _map_vbox_state(self, vbox_state: str) -> str:
        """Map VirtualBox state to our standard states"""
        state_map = {
            'running': 'running',
            'poweroff': 'stopped',
            'saved': 'suspended',
            'paused': 'suspended',
            'aborted': 'error'
        }
        return state_map.get(vbox_state.lower(), 'unknown')
