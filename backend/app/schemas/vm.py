from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class VMState(str, Enum):
    """VM lifecycle states"""
    CREATING = "creating"
    RUNNING = "running"
    STOPPED = "stopped"
    SUSPENDED = "suspended"
    ERROR = "error"
    DESTROYING = "destroying"
    UNKNOWN = "unknown"


class VMCreate(BaseModel):
    """Schema for creating a new VM"""
    name: str = Field(..., min_length=1, max_length=255, description="VM name")
    provider: str = Field(..., description="Provider name (e.g., 'proxmox', 'virtualbox')")
    template_id: Optional[int] = Field(None, description="Template ID to use")
    vagrantfile_content: Optional[str] = Field(None, description="Raw Vagrantfile content")
    config: Dict[str, Any] = Field(default_factory=dict, description="VM configuration")
    description: Optional[str] = Field(None, max_length=500)


class VMResponse(BaseModel):
    """Schema for VM response"""
    id: int
    name: str
    provider: str
    state: VMState
    config: Dict[str, Any]
    description: Optional[str]
    vagrantfile_path: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VMStatus(BaseModel):
    """Schema for VM status"""
    id: int
    name: str
    state: VMState
    provider_state: Optional[str] = None
    ip_address: Optional[str] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    uptime: Optional[int] = None
    last_checked: datetime
