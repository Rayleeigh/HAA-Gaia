from typing import Dict, Any, List, Optional
import asyncio
import subprocess
import json
import platform

from app.services.providers.base import BaseProvider, ProviderRegistry
from app.schemas.provider import ProviderStatus, ProviderType


@ProviderRegistry.register
class HyperVProvider(BaseProvider):
    """
    Microsoft Hyper-V provider.

    Supports creating and managing VMs using Windows Hyper-V.
    Uses PowerShell Hyper-V module for VM operations.
    Only available on Windows with Hyper-V enabled.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)

    @property
    def name(self) -> str:
        return "hyperv"

    @property
    def display_name(self) -> str:
        return "Hyper-V"

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.HYPERV

    async def check_status(self) -> ProviderStatus:
        """Check if Hyper-V is available"""
        # Check if running on Windows
        if platform.system() != "Windows":
            return ProviderStatus(
                name=self.name,
                available=False,
                configured=False,
                message="Hyper-V is only available on Windows"
            )

        try:
            # Check if Hyper-V module is available
            result = await self._run_powershell(
                "Get-Command Get-VM -ErrorAction Stop; $PSVersionTable.PSVersion.ToString()"
            )

            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[-1]
                return ProviderStatus(
                    name=self.name,
                    available=True,
                    configured=True,
                    version=version,
                    message="Hyper-V is available and configured",
                    details={"powershell_version": version}
                )
            else:
                return ProviderStatus(
                    name=self.name,
                    available=False,
                    configured=False,
                    message="Hyper-V module not found. Ensure Hyper-V is enabled."
                )

        except Exception as e:
            return ProviderStatus(
                name=self.name,
                available=False,
                configured=False,
                message=f"Error checking Hyper-V: {str(e)}"
            )

    async def create_vm(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new VM in Hyper-V"""
        vm_name = config.get('name')
        cpus = config.get('cpus', 2)
        memory = config.get('memory', 2048) * 1024 * 1024  # Convert MB to bytes
        generation = config.get('generation', 2)  # Generation 1 or 2

        try:
            # Create VM
            ps_script = f"""
            $vm = New-VM -Name '{vm_name}' -Generation {generation} -MemoryStartupBytes {memory}
            Set-VM -VM $vm -ProcessorCount {cpus}

            # Create virtual hard disk
            $vhdPath = Join-Path (Get-VMHost).VirtualHardDiskPath '{vm_name}.vhdx'
            New-VHD -Path $vhdPath -SizeBytes {config.get('disk_size_gb', 32)}GB -Dynamic
            Add-VMHardDiskDrive -VM $vm -Path $vhdPath

            # Add network adapter
            $switch = Get-VMSwitch | Select-Object -First 1
            if ($switch) {{
                Connect-VMNetworkAdapter -VM $vm -SwitchName $switch.Name
            }}

            Write-Output "SUCCESS:$($vm.Id)"
            """

            result = await self._run_powershell(ps_script)

            if "SUCCESS:" in result.stdout:
                vm_id = result.stdout.split("SUCCESS:")[-1].strip()
                return {
                    'provider_vm_id': vm_name,
                    'vm_id': vm_id,
                    'name': vm_name,
                    'status': 'created',
                    'cpus': cpus,
                    'memory': config.get('memory', 2048)
                }
            else:
                raise Exception("VM creation did not return success")

        except Exception as e:
            # Cleanup on failure
            try:
                await self._run_powershell(f"Remove-VM -Name '{vm_name}' -Force")
            except:
                pass
            raise Exception(f"Failed to create VM: {str(e)}")

    async def start_vm(self, vm_id: str) -> bool:
        """Start a VM"""
        try:
            result = await self._run_powershell(f"Start-VM -Name '{vm_id}'")
            return result.returncode == 0
        except Exception as e:
            print(f"Error starting VM: {e}")
            return False

    async def stop_vm(self, vm_id: str) -> bool:
        """Stop a VM"""
        try:
            # Try graceful shutdown first
            result = await self._run_powershell(
                f"Stop-VM -Name '{vm_id}' -Force"
            )
            return result.returncode == 0
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
            ps_script = f"""
            $vm = Get-VM -Name '{vm_id}'
            $vhds = $vm | Get-VMHardDiskDrive
            Remove-VM -Name '{vm_id}' -Force
            foreach ($vhd in $vhds) {{
                if (Test-Path $vhd.Path) {{
                    Remove-Item $vhd.Path -Force
                }}
            }}
            """

            result = await self._run_powershell(ps_script)
            return result.returncode == 0
        except Exception as e:
            print(f"Error deleting VM: {e}")
            return False

    async def get_vm_status(self, vm_id: str) -> Dict[str, Any]:
        """Get VM status"""
        try:
            ps_script = f"""
            $vm = Get-VM -Name '{vm_id}'
            $vmInfo = @{{
                State = $vm.State.ToString()
                CPUUsage = $vm.CPUUsage
                MemoryAssigned = $vm.MemoryAssigned
                MemoryDemand = $vm.MemoryDemand
                Uptime = $vm.Uptime.TotalSeconds
                Status = $vm.Status
            }}
            $vmInfo | ConvertTo-Json
            """

            result = await self._run_powershell(ps_script)

            if result.returncode == 0:
                info = json.loads(result.stdout)

                return {
                    'state': self._map_hyperv_state(info.get('State', 'Unknown')),
                    'provider_state': info.get('State'),
                    'cpu_usage': info.get('CPUUsage'),
                    'memory_usage': info.get('MemoryAssigned'),
                    'uptime': info.get('Uptime'),
                    'status': info.get('Status')
                }
            else:
                return {'state': 'unknown', 'error': 'Failed to get VM info'}

        except Exception as e:
            return {
                'state': 'unknown',
                'error': str(e)
            }

    async def list_vms(self) -> List[Dict[str, Any]]:
        """List all VMs"""
        try:
            ps_script = """
            Get-VM | Select-Object Name, State, Id | ConvertTo-Json
            """

            result = await self._run_powershell(ps_script)

            if result.returncode == 0 and result.stdout.strip():
                vms_data = json.loads(result.stdout)

                # Handle single VM case (not array)
                if isinstance(vms_data, dict):
                    vms_data = [vms_data]

                vms = []
                for vm_data in vms_data:
                    vms.append({
                        'provider_vm_id': vm_data['Name'],
                        'name': vm_data['Name'],
                        'vm_id': vm_data['Id'],
                        'status': self._map_hyperv_state(vm_data['State'])
                    })

                return vms
            else:
                return []

        except Exception as e:
            print(f"Error listing VMs: {e}")
            return []

    def get_capabilities(self) -> Dict[str, Any]:
        """Get Hyper-V provider capabilities"""
        return {
            "supports_snapshots": True,
            "supports_cloning": True,
            "supports_live_migration": True,
            "supports_networking": True,
            "supports_storage": True,
            "supports_provisioning": True,
            "supports_nested_virtualization": True,
            "supports_dynamic_memory": True
        }

    async def _run_powershell(self, script: str) -> subprocess.CompletedProcess:
        """Run PowerShell script"""
        result = await asyncio.to_thread(
            subprocess.run,
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            text=True,
            timeout=60
        )

        return result

    def _map_hyperv_state(self, hyperv_state: str) -> str:
        """Map Hyper-V state to our standard states"""
        state_map = {
            'Running': 'running',
            'Off': 'stopped',
            'Saved': 'suspended',
            'Paused': 'suspended',
            'Starting': 'creating',
            'Stopping': 'stopping'
        }
        return state_map.get(hyperv_state, 'unknown')
