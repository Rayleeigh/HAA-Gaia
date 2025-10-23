from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class TemplateCreate(BaseModel):
    """Schema for creating a new template"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    provider: str = Field(..., description="Target provider (e.g., 'proxmox', 'virtualbox')")
    config: Dict[str, Any] = Field(..., description="Template configuration")
    vagrantfile_template: Optional[str] = Field(None, description="Vagrantfile template content")
    is_public: bool = Field(default=False, description="Whether template is publicly available")
    tags: list[str] = Field(default_factory=list, description="Template tags")


class TemplateResponse(BaseModel):
    """Schema for template response"""
    id: int
    name: str
    description: Optional[str]
    provider: str
    config: Dict[str, Any]
    vagrantfile_template: Optional[str]
    is_public: bool
    tags: list[str]
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
