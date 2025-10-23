from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.vm import VMCreate, VMResponse, VMStatus
from app.services.vm_service import VMService

router = APIRouter()


@router.post("/", response_model=VMResponse, status_code=201)
async def create_vm(
    vm_data: VMCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new virtual machine"""
    vm_service = VMService(db)
    vm = await vm_service.create_vm(vm_data, background_tasks)
    return vm


@router.get("/", response_model=List[VMResponse])
async def list_vms(
    skip: int = 0,
    limit: int = 100,
    provider: str = None,
    db: Session = Depends(get_db)
):
    """List all virtual machines"""
    vm_service = VMService(db)
    vms = await vm_service.list_vms(skip=skip, limit=limit, provider=provider)
    return vms


@router.get("/{vm_id}", response_model=VMResponse)
async def get_vm(vm_id: int, db: Session = Depends(get_db)):
    """Get virtual machine details"""
    vm_service = VMService(db)
    vm = await vm_service.get_vm(vm_id)
    if not vm:
        raise HTTPException(status_code=404, detail="VM not found")
    return vm


@router.post("/{vm_id}/start")
async def start_vm(
    vm_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start a virtual machine"""
    vm_service = VMService(db)
    result = await vm_service.start_vm(vm_id, background_tasks)
    return result


@router.post("/{vm_id}/stop")
async def stop_vm(
    vm_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Stop a virtual machine"""
    vm_service = VMService(db)
    result = await vm_service.stop_vm(vm_id, background_tasks)
    return result


@router.delete("/{vm_id}")
async def delete_vm(
    vm_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Delete a virtual machine"""
    vm_service = VMService(db)
    result = await vm_service.delete_vm(vm_id, background_tasks)
    return result


@router.get("/{vm_id}/status", response_model=VMStatus)
async def get_vm_status(vm_id: int, db: Session = Depends(get_db)):
    """Get virtual machine status"""
    vm_service = VMService(db)
    status = await vm_service.get_vm_status(vm_id)
    return status
