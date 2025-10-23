from typing import Dict, Any, List, Optional
import asyncio
import subprocess
import json
import platform
import re

from app.services.providers.base import BaseProvider, ProviderRegistry
from app.schemas.provider import ProviderStatus, ProviderType


@ProviderRegistry.register
class WSLProvider(BaseProvider):
    """
    Windows Subsystem for Linux (WSL) provider.

    Supports creating and managing WSL2 distributions.
    Uses wsl.exe CLI for distribution management.
    Only available on Windows 10/11 with WSL2 enabled.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)

    @property
    def name(self) -> str:
        return "wsl"

    @property
    def display_name(self) -> str:
        return "WSL2"

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.WSL

    async def check_status(self) -> ProviderStatus:
        """Check if WSL is available"""
        # Check if running on Windows
        if platform.system() != "Windows":
            return ProviderStatus(
                name=self.name,
                available=False,
                configured=False,
                message="WSL is only available on Windows"
            )

        try:
            # Check WSL version
            result = await self._run_wsl(["--version"])

            if result.returncode == 0:
                version_info = result.stdout.strip()
                # Extract WSL version
                version_match = re.search(r'WSL version: ([\d.]+)', version_info)
                version = version_match.group(1) if version_match else "Unknown"

                # Check if WSL2 is default
                status_result = await self._run_wsl(["--status"])
                is_wsl2 = "Default Version: 2" in status_result.stdout or "WSL 2" in status_result.stdout

                return ProviderStatus(
                    name=self.name,
                    available=True,
                    configured=is_wsl2,
                    version=version,
                    message=f"WSL {version} is available" + (" (WSL2 enabled)" if is_wsl2 else " (WSL2 not default)"),
                    details={"wsl2_enabled": is_wsl2}
                )
            else:
                return ProviderStatus(
                    name=self.name,
                    available=False,
                    configured=False,
                    message="WSL is not responding properly"
                )

        except FileNotFoundError:
            return ProviderStatus(
                name=self.name,
                available=False,
                configured=False,
                message="WSL is not installed or not available"
            )
        except Exception as e:
            return ProviderStatus(
                name=self.name,
                available=False,
                configured=False,
                message=f"Error checking WSL: {str(e)}"
            )

    async def create_vm(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new WSL distribution"""
        distro_name = config.get('name')
        base_distro = config.get('base_distro', 'Ubuntu')  # Ubuntu, Debian, etc.
        install_location = config.get('install_location')

        try:
            # For WSL, we need to either:
            # 1. Import a tar file
            # 2. Clone an existing distribution
            # 3. Install from Microsoft Store (requires user interaction)

            # Check if a tarball path is provided
            tarball = config.get('tarball')
            if tarball:
                # Import from tarball
                cmd = ["--import", distro_name, install_location, tarball]
                if config.get('version') == 2:
                    cmd.append("--version")
                    cmd.append("2")

                result = await self._run_wsl(cmd)

                if result.returncode != 0:
                    raise Exception(f"Failed to import distribution: {result.stderr}")

            else:
                # Clone from existing distribution
                source_distro = config.get('source_distro', 'Ubuntu')

                # Check if source exists
                distros = await self.list_vms()
                source_exists = any(d['name'] == source_distro for d in distros)

                if not source_exists:
                    raise Exception(f"Source distribution '{source_distro}' not found. Please provide a tarball path.")

                # Export source distro to temp file
                import tempfile
                import os

                with tempfile.NamedTemporaryFile(suffix='.tar', delete=False) as temp_file:
                    temp_path = temp_file.name

                try:
                    # Export source
                    export_result = await self._run_wsl([
                        "--export", source_distro, temp_path
                    ])

                    if export_result.returncode != 0:
                        raise Exception(f"Failed to export source: {export_result.stderr}")

                    # Import as new distro
                    import_cmd = ["--import", distro_name, install_location or f"C:\\WSL\\{distro_name}", temp_path, "--version", "2"]
                    import_result = await self._run_wsl(import_cmd)

                    if import_result.returncode != 0:
                        raise Exception(f"Failed to import distribution: {import_result.stderr}")

                finally:
                    # Clean up temp file
                    try:
                        os.unlink(temp_path)
                    except:
                        pass

            # Set default user if specified
            default_user = config.get('default_user')
            if default_user:
                await self._run_wsl([
                    "-d", distro_name,
                    "-u", "root",
                    "--", "useradd", "-m", "-s", "/bin/bash", default_user
                ])

            return {
                'provider_vm_id': distro_name,
                'name': distro_name,
                'status': 'created',
                'base_distro': base_distro
            }

        except Exception as e:
            # Cleanup on failure
            try:
                await self._run_wsl(["--unregister", distro_name])
            except:
                pass
            raise Exception(f"Failed to create WSL distribution: {str(e)}")

    async def start_vm(self, vm_id: str) -> bool:
        """Start a WSL distribution (distributions auto-start when accessed)"""
        try:
            # WSL distributions auto-start when accessed
            # We can verify by running a simple command
            result = await self._run_wsl([
                "-d", vm_id,
                "--", "echo", "started"
            ])
            return result.returncode == 0
        except Exception as e:
            print(f"Error starting WSL distribution: {e}")
            return False

    async def stop_vm(self, vm_id: str) -> bool:
        """Stop a WSL distribution"""
        try:
            result = await self._run_wsl([
                "--terminate", vm_id
            ])
            return result.returncode == 0
        except Exception as e:
            print(f"Error stopping WSL distribution: {e}")
            return False

    async def delete_vm(self, vm_id: str) -> bool:
        """Delete a WSL distribution"""
        try:
            # Terminate first
            await self.stop_vm(vm_id)

            # Unregister (deletes the distribution)
            result = await self._run_wsl([
                "--unregister", vm_id
            ])
            return result.returncode == 0
        except Exception as e:
            print(f"Error deleting WSL distribution: {e}")
            return False

    async def get_vm_status(self, vm_id: str) -> Dict[str, Any]:
        """Get WSL distribution status"""
        try:
            # List running distributions
            result = await self._run_wsl([
                "--list", "--running"
            ])

            is_running = vm_id in result.stdout

            # Get distribution info
            info_result = await self._run_wsl([
                "--list", "--verbose"
            ])

            # Parse verbose output to find our distro
            distro_info = {}
            for line in info_result.stdout.split('\n'):
                if vm_id in line:
                    # Format: NAME STATE VERSION
                    parts = line.split()
                    if len(parts) >= 3:
                        distro_info['state'] = parts[1]
                        distro_info['version'] = parts[2]

            return {
                'state': 'running' if is_running else 'stopped',
                'provider_state': distro_info.get('state', 'Unknown'),
                'wsl_version': distro_info.get('version', 'Unknown'),
                'name': vm_id
            }

        except Exception as e:
            return {
                'state': 'unknown',
                'error': str(e)
            }

    async def list_vms(self) -> List[Dict[str, Any]]:
        """List all WSL distributions"""
        try:
            result = await self._run_wsl([
                "--list", "--verbose"
            ])

            vms = []
            lines = result.stdout.split('\n')[1:]  # Skip header

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Remove BOM and special characters
                line = line.replace('\x00', '').replace('*', '').strip()

                # Parse: NAME STATE VERSION
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[0]
                    state = parts[1]
                    version = parts[2]

                    vms.append({
                        'provider_vm_id': name,
                        'name': name,
                        'status': 'running' if state.lower() == 'running' else 'stopped',
                        'wsl_version': version
                    })

            return vms

        except Exception as e:
            print(f"Error listing WSL distributions: {e}")
            return []

    def get_capabilities(self) -> Dict[str, Any]:
        """Get WSL provider capabilities"""
        return {
            "supports_snapshots": False,
            "supports_cloning": True,
            "supports_live_migration": False,
            "supports_networking": True,
            "supports_storage": True,
            "supports_provisioning": True,
            "supports_gui": True,  # WSLg support
            "supports_docker": True,
            "supports_systemd": True  # WSL2 supports systemd
        }

    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate WSL configuration"""
        # WSL requires either a tarball or source_distro
        if not config.get('tarball') and not config.get('source_distro'):
            return False, "WSL distribution requires either 'tarball' or 'source_distro' to be specified"

        return True, None

    async def _run_wsl(self, args: List[str]) -> subprocess.CompletedProcess:
        """Run wsl.exe command"""
        result = await asyncio.to_thread(
            subprocess.run,
            ["wsl"] + args,
            capture_output=True,
            text=True,
            timeout=60
        )

        return result
