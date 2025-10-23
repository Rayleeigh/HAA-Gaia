# HAA-Gaia Provider Documentation

This document provides detailed information about each virtualization provider supported by HAA-Gaia.

## Table of Contents

- [Proxmox VE](#proxmox-ve)
- [VirtualBox](#virtualbox)
- [Hyper-V](#hyper-v)
- [WSL2](#wsl2)
- [Adding New Providers](#adding-new-providers)

---

## Proxmox VE

**Status:** ✅ Fully Implemented (MVP)

### Description
Proxmox Virtual Environment is an open-source server virtualization platform that combines KVM hypervisor and LXC containers.

### Requirements
- Proxmox VE 7.0 or later
- API access credentials
- Network connectivity to Proxmox host

### Configuration

Add the following to your `backend/.env`:

```env
PROXMOX_HOST=your-proxmox-host.com
PROXMOX_USER=root@pam
PROXMOX_PASSWORD=your-password
PROXMOX_VERIFY_SSL=false
```

### Features

- ✅ Create/Delete VMs
- ✅ Start/Stop/Suspend VMs
- ✅ Status monitoring
- ✅ Resource allocation (CPU, Memory, Disk)
- ✅ Network configuration
- ✅ Storage management
- ✅ Snapshots
- ✅ Live migration
- ✅ High availability

### Example Configuration

```json
{
  "name": "my-proxmox-vm",
  "provider": "proxmox",
  "config": {
    "box": "generic/ubuntu2204",
    "hostname": "ubuntu-server",
    "cpus": 4,
    "memory": 8192,
    "provider_config": {
      "node": "pve",
      "storage": "local-lvm",
      "disk_size": "64G",
      "ostype": "l26"
    }
  }
}
```

### Limitations

- Requires Proxmox VE API access
- Network configuration depends on Proxmox network setup
- Some advanced features require Proxmox subscription

---

## VirtualBox

**Status:** ✅ Fully Implemented

### Description
Oracle VirtualBox is a free and open-source hosted hypervisor for x86 virtualization.

### Requirements
- VirtualBox 6.1 or later installed
- VBoxManage CLI available in PATH
- Sufficient disk space and system resources

### Installation

**Windows:**
```powershell
choco install virtualbox
```

**macOS:**
```bash
brew install --cask virtualbox
```

**Linux:**
```bash
sudo apt-get install virtualbox
```

### Features

- ✅ Create/Delete VMs
- ✅ Start/Stop/Pause VMs
- ✅ Headless and GUI modes
- ✅ Snapshots and cloning
- ✅ Shared folders
- ✅ Network configuration
- ✅ Guest additions support
- ✅ Cross-platform support

### Example Configuration

```json
{
  "name": "my-virtualbox-vm",
  "provider": "virtualbox",
  "config": {
    "box": "bento/ubuntu-22.04",
    "hostname": "ubuntu-dev",
    "cpus": 2,
    "memory": 4096,
    "disk_size": 32768,
    "provider_config": {
      "gui": false,
      "vram": 128,
      "accelerate3d": "on",
      "clipboard": "bidirectional",
      "draganddrop": "bidirectional"
    },
    "networks": [
      {
        "type": "private_network",
        "ip": "192.168.56.10"
      },
      {
        "type": "forwarded_port",
        "guest_port": 22,
        "host_port": 2222
      }
    ]
  }
}
```

### Limitations

- Requires VirtualBox to be installed on host
- Performance lower than Type-1 hypervisors
- Limited enterprise features
- GUI mode only available on desktop systems

---

## Hyper-V

**Status:** ✅ Fully Implemented

### Description
Microsoft Hyper-V is a native hypervisor that can create virtual machines on Windows systems.

### Requirements
- Windows 10 Pro/Enterprise or Windows Server
- Hyper-V feature enabled
- PowerShell with Hyper-V module
- Administrator privileges

### Enabling Hyper-V

**Windows 10/11:**
```powershell
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```

**Windows Server:**
```powershell
Install-WindowsFeature -Name Hyper-V -IncludeManagementTools -Restart
```

### Features

- ✅ Create/Delete VMs
- ✅ Start/Stop/Save VMs
- ✅ Generation 1 and 2 VMs
- ✅ Dynamic memory
- ✅ Nested virtualization
- ✅ Checkpoints (snapshots)
- ✅ Live migration
- ✅ Integration services

### Example Configuration

```json
{
  "name": "my-hyperv-vm",
  "provider": "hyperv",
  "config": {
    "box": "bento/ubuntu-22.04",
    "hostname": "ubuntu-hyperv",
    "cpus": 2,
    "memory": 4096,
    "generation": 2,
    "disk_size_gb": 64,
    "provider_config": {
      "enable_virtualization_extensions": true,
      "linked_clone": true,
      "differencing_disk": true,
      "vm_integration_services": {
        "guest_service_interface": true,
        "heartbeat": true,
        "time_synchronization": true
      }
    }
  }
}
```

### Limitations

- Windows-only (Windows 10 Pro+ or Windows Server)
- Cannot run simultaneously with VirtualBox
- Requires administrator privileges
- Some features require specific Windows versions

### Troubleshooting

**Hyper-V and VirtualBox Conflict:**
Hyper-V and VirtualBox cannot run simultaneously. To switch between them:

```powershell
# Disable Hyper-V
bcdedit /set hypervisorlaunchtype off
# Restart

# Enable Hyper-V
bcdedit /set hypervisorlaunchtype auto
# Restart
```

---

## WSL2

**Status:** ✅ Fully Implemented

### Description
Windows Subsystem for Linux 2 (WSL2) allows running Linux distributions natively on Windows using a lightweight virtual machine.

### Requirements
- Windows 10 version 2004+ or Windows 11
- WSL2 installed and enabled
- At least one Linux distribution installed

### Installation

```powershell
# Install WSL
wsl --install

# Set WSL2 as default
wsl --set-default-version 2

# List available distributions
wsl --list --online

# Install a distribution
wsl --install -d Ubuntu-22.04
```

### Features

- ✅ Create distributions (import/clone)
- ✅ Start/Stop distributions
- ✅ Delete distributions
- ✅ Custom configuration
- ✅ WSLg (GUI apps)
- ✅ Docker integration
- ✅ systemd support
- ✅ Fast startup times

### Example Configuration

```json
{
  "name": "Ubuntu-Dev",
  "provider": "wsl",
  "config": {
    "base_distro": "Ubuntu",
    "source_distro": "Ubuntu-22.04",
    "install_location": "C:\\WSL\\Ubuntu-Dev",
    "default_user": "developer",
    "provisioners": [
      {
        "type": "shell",
        "inline": [
          "apt-get update",
          "apt-get install -y build-essential git docker.io",
          "usermod -aG docker $USER"
        ]
      }
    ]
  }
}
```

### Creating from Tarball

To create a WSL distribution from a tarball:

```json
{
  "name": "Custom-Linux",
  "provider": "wsl",
  "config": {
    "tarball": "C:\\path\\to\\rootfs.tar",
    "install_location": "C:\\WSL\\Custom-Linux",
    "default_user": "user"
  }
}
```

### Limitations

- Windows-only (Windows 10/11)
- Requires WSL2 to be enabled
- Limited to Linux distributions
- No traditional VM features (snapshots, etc.)
- Distributions share kernel with host WSL2 VM

### Best Practices

1. **Use WSL2:** Always use WSL2 over WSL1 for better performance
2. **Store in /home:** Keep project files in Linux filesystem for better performance
3. **Docker Desktop:** Use Docker Desktop for Windows with WSL2 backend
4. **VS Code:** Use VS Code Remote-WSL extension for development

### Useful Commands

```bash
# List all distributions
wsl --list --verbose

# Set default distribution
wsl --set-default Ubuntu-Dev

# Access distribution
wsl -d Ubuntu-Dev

# Stop distribution
wsl --terminate Ubuntu-Dev

# Export distribution
wsl --export Ubuntu-Dev backup.tar

# Import distribution
wsl --import NewUbuntu C:\WSL\NewUbuntu backup.tar

# Unregister (delete) distribution
wsl --unregister Ubuntu-Dev
```

---

## Provider Comparison

| Feature | Proxmox | VirtualBox | Hyper-V | WSL2 |
|---------|---------|------------|---------|------|
| **Platform** | Linux Server | Cross-platform | Windows | Windows |
| **Type** | Type-1 | Type-2 | Type-1 | Hybrid |
| **Cost** | Open Source | Free | Free | Free |
| **GUI Support** | ✅ | ✅ | ✅ | ✅ (WSLg) |
| **Snapshots** | ✅ | ✅ | ✅ | ❌ |
| **Live Migration** | ✅ | ❌ | ✅ | ❌ |
| **Nested Virtualization** | ✅ | ✅ | ✅ | ❌ |
| **Best For** | Enterprise/Production | Development | Windows Enterprise | Linux Development |
| **Performance** | Excellent | Good | Excellent | Excellent |
| **Resource Usage** | Medium | High | Low | Very Low |

---

## Adding New Providers

To add a new provider to HAA-Gaia:

### 1. Create Provider Class

Create a new file in `backend/app/services/providers/`:

```python
from app.services.providers.base import BaseProvider, ProviderRegistry
from app.schemas.provider import ProviderType, ProviderStatus

@ProviderRegistry.register
class MyProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "myprovider"

    @property
    def display_name(self) -> str:
        return "My Provider"

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.MYPROVIDER

    async def check_status(self) -> ProviderStatus:
        # Check if provider is available
        pass

    async def create_vm(self, config: Dict[str, Any]) -> Dict[str, Any]:
        # Create VM implementation
        pass

    async def start_vm(self, vm_id: str) -> bool:
        # Start VM implementation
        pass

    async def stop_vm(self, vm_id: str) -> bool:
        # Stop VM implementation
        pass

    async def delete_vm(self, vm_id: str) -> bool:
        # Delete VM implementation
        pass

    async def get_vm_status(self, vm_id: str) -> Dict[str, Any]:
        # Get VM status
        pass

    async def list_vms(self) -> List[Dict[str, Any]]:
        # List VMs
        pass
```

### 2. Update Provider Schema

Add your provider type to `backend/app/schemas/provider.py`:

```python
class ProviderType(str, Enum):
    PROXMOX = "proxmox"
    VIRTUALBOX = "virtualbox"
    HYPERV = "hyperv"
    WSL = "wsl"
    MYPROVIDER = "myprovider"  # Add here
```

### 3. Add Vagrantfile Generator

Add a generator method in `backend/app/services/vagrant/generator.py`:

```python
def generate_myprovider(self, config: Dict[str, Any]) -> str:
    """Generate a MyProvider-specific Vagrantfile"""
    template_str = '''# Your provider template'''
    template = Template(template_str)
    return template.render(config)
```

### 4. Update VM Service

Update `backend/app/services/vm_service.py` to use your generator:

```python
generator_map = {
    'proxmox': self.vagrant_generator.generate_proxmox,
    'virtualbox': self.vagrant_generator.generate_virtualbox,
    'hyperv': self.vagrant_generator.generate_hyperv,
    'wsl': self.vagrant_generator.generate_wsl,
    'myprovider': self.vagrant_generator.generate_myprovider,  # Add here
}
```

### 5. Create Templates

Create example templates in `templates/`:

```yaml
name: "Example VM - MyProvider"
description: "Example configuration for MyProvider"
provider: myprovider
config:
  # Your configuration
```

### 6. Document Your Provider

Add documentation to this file with:
- Requirements
- Installation instructions
- Features
- Example configurations
- Limitations
- Troubleshooting

---

## Support

For provider-specific issues:
- **Proxmox:** Check Proxmox VE documentation and API logs
- **VirtualBox:** Run `VBoxManage list vms` to verify installation
- **Hyper-V:** Verify `Get-VM` works in PowerShell
- **WSL:** Run `wsl --status` to check WSL configuration

For HAA-Gaia issues:
- [GitHub Issues](https://github.com/Rayleeigh/HAA-Gaia/issues)
- [Discussions](https://github.com/Rayleeigh/HAA-Gaia/discussions)
