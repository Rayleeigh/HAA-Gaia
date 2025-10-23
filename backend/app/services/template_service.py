from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.template import Template
from app.schemas.template import TemplateCreate, TemplateResponse
from app.services.vagrant.parser import VagrantfileParser


class TemplateService:
    """Service for managing VM templates"""

    def __init__(self, db: Session):
        self.db = db
        self.parser = VagrantfileParser()

    async def create_template(self, template_data: TemplateCreate) -> Template:
        """Create a new template"""

        # Check if template name already exists
        existing = self.db.query(Template).filter(Template.name == template_data.name).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Template '{template_data.name}' already exists")

        template = Template(
            name=template_data.name,
            description=template_data.description,
            provider=template_data.provider,
            config=template_data.config,
            vagrantfile_template=template_data.vagrantfile_template,
            is_public=template_data.is_public,
            tags=template_data.tags
        )

        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)

        return template

    async def list_templates(self, skip: int = 0, limit: int = 100, provider: str = None) -> List[Template]:
        """List templates"""
        query = self.db.query(Template)

        if provider:
            query = query.filter(Template.provider == provider)

        return query.offset(skip).limit(limit).all()

    async def get_template(self, template_id: int) -> Optional[Template]:
        """Get template by ID"""
        return self.db.query(Template).filter(Template.id == template_id).first()

    async def update_template(self, template_id: int, template_data: TemplateCreate) -> Optional[Template]:
        """Update a template"""
        template = await self.get_template(template_id)
        if not template:
            return None

        template.name = template_data.name
        template.description = template_data.description
        template.provider = template_data.provider
        template.config = template_data.config
        template.vagrantfile_template = template_data.vagrantfile_template
        template.is_public = template_data.is_public
        template.tags = template_data.tags

        self.db.commit()
        self.db.refresh(template)

        return template

    async def delete_template(self, template_id: int) -> bool:
        """Delete a template"""
        template = await self.get_template(template_id)
        if not template:
            return False

        self.db.delete(template)
        self.db.commit()

        return True

    async def import_from_vagrantfile(self, vagrantfile_content: str) -> Template:
        """Import a template from an existing Vagrantfile"""

        # Parse the Vagrantfile
        config = self.parser.parse(vagrantfile_content)

        # Create template from parsed config
        template_data = TemplateCreate(
            name=f"Imported - {config.get('hostname', config.get('box', 'unknown'))}",
            description="Imported from Vagrantfile",
            provider=config.get('provider', 'virtualbox'),
            config=config,
            vagrantfile_template=vagrantfile_content,
            is_public=False,
            tags=['imported']
        )

        return await self.create_template(template_data)
