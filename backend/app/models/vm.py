from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base
from app.schemas.vm import VMState


class VirtualMachine(Base):
    """Virtual Machine model"""
    __tablename__ = "virtual_machines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)
    state = Column(SQLEnum(VMState), default=VMState.CREATING, nullable=False)
    config = Column(JSON, nullable=False, default={})
    description = Column(String(500), nullable=True)
    vagrantfile_path = Column(String(500), nullable=True)
    provider_vm_id = Column(String(255), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<VirtualMachine(id={self.id}, name='{self.name}', provider='{self.provider}', state='{self.state}')>"
