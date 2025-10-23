from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, ARRAY
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base


class Template(Base):
    """VM Template model"""
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True, unique=True)
    description = Column(String(500), nullable=True)
    provider = Column(String(50), nullable=False, index=True)
    config = Column(JSON, nullable=False, default={})
    vagrantfile_template = Column(String, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    tags = Column(ARRAY(String), nullable=False, default=[])
    usage_count = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.name}', provider='{self.provider}')>"
