from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.template import TemplateCreate, TemplateResponse
from app.services.template_service import TemplateService

router = APIRouter()


@router.post("/", response_model=TemplateResponse, status_code=201)
async def create_template(
    template_data: TemplateCreate,
    db: Session = Depends(get_db)
):
    """Create a new VM template"""
    template_service = TemplateService(db)
    template = await template_service.create_template(template_data)
    return template


@router.get("/", response_model=List[TemplateResponse])
async def list_templates(
    skip: int = 0,
    limit: int = 100,
    provider: str = None,
    db: Session = Depends(get_db)
):
    """List all templates"""
    template_service = TemplateService(db)
    templates = await template_service.list_templates(skip=skip, limit=limit, provider=provider)
    return templates


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: int, db: Session = Depends(get_db)):
    """Get template details"""
    template_service = TemplateService(db)
    template = await template_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template_data: TemplateCreate,
    db: Session = Depends(get_db)
):
    """Update a template"""
    template_service = TemplateService(db)
    template = await template_service.update_template(template_id, template_data)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.delete("/{template_id}")
async def delete_template(template_id: int, db: Session = Depends(get_db)):
    """Delete a template"""
    template_service = TemplateService(db)
    result = await template_service.delete_template(template_id)
    if not result:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted successfully"}


@router.post("/import")
async def import_template(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import a template from a Vagrantfile"""
    template_service = TemplateService(db)
    content = await file.read()
    template = await template_service.import_from_vagrantfile(content.decode('utf-8'))
    return template
