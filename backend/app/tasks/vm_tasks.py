from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.vm import VirtualMachine
from app.schemas.vm import VMState
from app.services.providers.base import ProviderRegistry
from typing import Dict, Any
import asyncio


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, will be closed in task


@celery_app.task(bind=True, name="create_vm")
def create_vm_task(self, vm_id: int, config: Dict[str, Any]):
    """Celery task to create a VM"""
    db = get_db()

    try:
        vm = db.query(VirtualMachine).filter(VirtualMachine.id == vm_id).first()
        if not vm:
            return {"error": "VM not found"}

        # Get provider
        provider = ProviderRegistry.get_provider(vm.provider, config.get('provider_config'))

        # Create VM using provider
        result = asyncio.run(provider.create_vm(config))

        # Update VM record
        vm.provider_vm_id = result.get('provider_vm_id')
        vm.state = VMState.STOPPED
        vm.config = {**vm.config, **result}

        db.commit()

        return {"status": "success", "vm_id": vm_id, "provider_vm_id": vm.provider_vm_id}

    except Exception as e:
        # Mark VM as error state
        vm = db.query(VirtualMachine).filter(VirtualMachine.id == vm_id).first()
        if vm:
            vm.state = VMState.ERROR
            db.commit()

        return {"status": "error", "message": str(e)}

    finally:
        db.close()


@celery_app.task(bind=True, name="start_vm")
def start_vm_task(self, vm_id: int):
    """Celery task to start a VM"""
    db = get_db()

    try:
        vm = db.query(VirtualMachine).filter(VirtualMachine.id == vm_id).first()
        if not vm:
            return {"error": "VM not found"}

        # Get provider
        provider = ProviderRegistry.get_provider(vm.provider)

        # Start VM
        success = asyncio.run(provider.start_vm(vm.provider_vm_id))

        if success:
            vm.state = VMState.RUNNING
            db.commit()
            return {"status": "success", "vm_id": vm_id}
        else:
            return {"status": "error", "message": "Failed to start VM"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        db.close()


@celery_app.task(bind=True, name="stop_vm")
def stop_vm_task(self, vm_id: int):
    """Celery task to stop a VM"""
    db = get_db()

    try:
        vm = db.query(VirtualMachine).filter(VirtualMachine.id == vm_id).first()
        if not vm:
            return {"error": "VM not found"}

        # Get provider
        provider = ProviderRegistry.get_provider(vm.provider)

        # Stop VM
        success = asyncio.run(provider.stop_vm(vm.provider_vm_id))

        if success:
            vm.state = VMState.STOPPED
            db.commit()
            return {"status": "success", "vm_id": vm_id}
        else:
            return {"status": "error", "message": "Failed to stop VM"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        db.close()


@celery_app.task(bind=True, name="delete_vm")
def delete_vm_task(self, vm_id: int):
    """Celery task to delete a VM"""
    db = get_db()

    try:
        vm = db.query(VirtualMachine).filter(VirtualMachine.id == vm_id).first()
        if not vm:
            return {"error": "VM not found"}

        # Get provider
        provider = ProviderRegistry.get_provider(vm.provider)

        # Delete VM from provider
        success = asyncio.run(provider.delete_vm(vm.provider_vm_id))

        if success:
            # Delete from database
            db.delete(vm)
            db.commit()
            return {"status": "success", "vm_id": vm_id}
        else:
            return {"status": "error", "message": "Failed to delete VM"}

    except Exception as e:
        # Still delete from database even if provider deletion failed
        vm = db.query(VirtualMachine).filter(VirtualMachine.id == vm_id).first()
        if vm:
            db.delete(vm)
            db.commit()

        return {"status": "partial", "message": f"Deleted from DB but provider error: {str(e)}"}

    finally:
        db.close()
