from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class NetworkConfig(BaseModel):
    """Network configuration for VM"""
    type: str = Field(..., description="Network type: private_network, public_network, forwarded_port")
    ip: Optional[str] = None
    bridge: Optional[str] = None
    guest_port: Optional[int] = None
    host_port: Optional[int] = None


class SyncedFolder(BaseModel):
    """Synced folder configuration"""
    host_path: str
    guest_path: str
    type: Optional[str] = Field(None, description="Sync type: nfs, rsync, smb, virtualbox")
    options: Dict[str, Any] = Field(default_factory=dict)


class ProvisionerConfig(BaseModel):
    """Provisioner configuration"""
    type: str = Field(..., description="Provisioner type: shell, ansible, puppet, chef")
    inline: Optional[List[str]] = None
    path: Optional[str] = None
    playbook: Optional[str] = None
    args: Optional[List[str]] = None


class VagrantfileConfig(BaseModel):
    """Complete Vagrantfile configuration"""
    box: str = Field(..., description="Base box name")
    box_version: Optional[str] = None
    box_url: Optional[str] = None
    hostname: Optional[str] = None

    # Provider-specific
    provider: str = Field(default="virtualbox", description="Provider name")
    provider_config: Dict[str, Any] = Field(default_factory=dict)

    # Resources
    cpus: Optional[int] = Field(None, ge=1, le=128)
    memory: Optional[int] = Field(None, ge=512, description="Memory in MB")

    # Networking
    networks: List[NetworkConfig] = Field(default_factory=list)

    # Synced folders
    synced_folders: List[SyncedFolder] = Field(default_factory=list)

    # Provisioning
    provisioners: List[ProvisionerConfig] = Field(default_factory=list)

    # Custom configuration
    custom_config: Optional[str] = Field(None, description="Raw Ruby code to inject")
