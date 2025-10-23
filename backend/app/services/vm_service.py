from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks, HTTPException

from app.models.vm import VirtualMachine
from app.schemas.vm import VMCreate, VMResponse, VMStatus, VMState
from app.services.providers.base import ProviderRegistry
from app.services.vagrant.generator import VagrantfileGenerator
from app.tasks.vm_tasks import create_vm_task, start_vm_task, stop_vm_task, delete_vm_task
import os


class VMService:
    """Service for managing virtual machines"""

    def __init__(self, db: Session):
        self.db = db
        self.vagrant_generator = VagrantfileGenerator()

    async def create_vm(self, vm_data: VMCreate, background_tasks: BackgroundTasks) -> VirtualMachine:
        """Create a new virtual machine"""

        # Validate provider
        provider = ProviderRegistry.get_provider(vm_data.provider)
        if not provider:
            raise HTTPException(status_code=400, detail=f"Provider '{vm_data.provider}' not found")

        # Create database record
        vm = VirtualMachine(
            name=vm_data.name,
            provider=vm_data.provider,
            state=VMState.CREATING,
            config=vm_data.config,
            description=vm_data.description
        )

        self.db.add(vm)
        self.db.commit()
        self.db.refresh(vm)

        # Generate Vagrantfile if not provided
        if not vm_data.vagrantfile_content:
            vagrantfile_content = self._generate_vagrantfile(vm_data)
        else:
            vagrantfile_content = vm_data.vagrantfile_content

        # Save Vagrantfile
        vagrantfile_path = self._save_vagrantfile(vm.id, vagrantfile_content)
        vm.vagrantfile_path = vagrantfile_path
        self.db.commit()

        # Queue async creation task
        background_tasks.add_task(create_vm_task, vm.id, vm_data.config)

        return vm

    async def list_vms(self, skip: int = 0, limit: int = 100, provider: str = None) -> List[VirtualMachine]:
        """List virtual machines"""
        query = self.db.query(VirtualMachine)

        if provider:
            query = query.filter(VirtualMachine.provider == provider)

        return query.offset(skip).limit(limit).all()

    async def get_vm(self, vm_id: int) -> Optional[VirtualMachine]:
        """Get a virtual machine by ID"""
        return self.db.query(VirtualMachine).filter(VirtualMachine.id == vm_id).first()

    async def start_vm(self, vm_id: int, background_tasks: BackgroundTasks) -> dict:
        """Start a virtual machine"""
        vm = await self.get_vm(vm_id)
        if not vm:
            raise HTTPException(status_code=404, detail="VM not found")

        if vm.state == VMState.RUNNING:
            return {"message": "VM is already running"}

        # Update state
        vm.state = VMState.RUNNING
        self.db.commit()

        # Queue async start task
        background_tasks.add_task(start_vm_task, vm_id)

        return {"message": f"Starting VM '{vm.name}'"}

    async def stop_vm(self, vm_id: int, background_tasks: BackgroundTasks) -> dict:
        """Stop a virtual machine"""
        vm = await self.get_vm(vm_id)
        if not vm:
            raise HTTPException(status_code=404, detail="VM not found")

        if vm.state == VMState.STOPPED:
            return {"message": "VM is already stopped"}

        # Queue async stop task
        background_tasks.add_task(stop_vm_task, vm_id)

        return {"message": f"Stopping VM '{vm.name}'"}

    async def delete_vm(self, vm_id: int, background_tasks: BackgroundTasks) -> dict:
        """Delete a virtual machine"""
        vm = await self.get_vm(vm_id)
        if not vm:
            raise HTTPException(status_code=404, detail="VM not found")

        # Update state
        vm.state = VMState.DESTROYING
        self.db.commit()

        # Queue async delete task
        background_tasks.add_task(delete_vm_task, vm_id)

        return {"message": f"Deleting VM '{vm.name}'"}

    async def get_vm_status(self, vm_id: int) -> VMStatus:
        """Get VM status"""
        vm = await self.get_vm(vm_id)
        if not vm:
            raise HTTPException(status_code=404, detail="VM not found")

        # Get status from provider if VM is created
        provider = ProviderRegistry.get_provider(vm.provider)
        if provider and vm.provider_vm_id:
            try:
                provider_status = await provider.get_vm_status(vm.provider_vm_id)

                return VMStatus(
                    id=vm.id,
                    name=vm.name,
                    state=vm.state,
                    provider_state=provider_status.get('provider_state'),
                    ip_address=provider_status.get('ip_address'),
                    cpu_usage=provider_status.get('cpu_usage'),
                    memory_usage=provider_status.get('memory_usage'),
                    uptime=provider_status.get('uptime'),
                    last_checked=provider_status.get('last_checked')
                )
            except Exception as e:
                print(f"Error getting provider status: {e}")

        # Return basic status if provider unavailable
        from datetime import datetime
        return VMStatus(
            id=vm.id,
            name=vm.name,
            state=vm.state,
            last_checked=datetime.now()
        )

    def _generate_vagrantfile(self, vm_data: VMCreate) -> str:
        """Generate Vagrantfile from VM configuration"""
        config = vm_data.config.copy()
        config['name'] = vm_data.name
        config['provider'] = vm_data.provider

        # Use provider-specific generator methods
        generator_map = {
            'proxmox': self.vagrant_generator.generate_proxmox,
            'virtualbox': self.vagrant_generator.generate_virtualbox,
            'hyperv': self.vagrant_generator.generate_hyperv,
            'wsl': self.vagrant_generator.generate_wsl,
        }

        generator = generator_map.get(vm_data.provider, self.vagrant_generator.generate)
        return generator(config)

    def _save_vagrantfile(self, vm_id: int, content: str) -> str:
        """Save Vagrantfile to disk"""
        # Create directory for VM
        vm_dir = os.path.join('vagrantfiles', str(vm_id))
        os.makedirs(vm_dir, exist_ok=True)

        # Save Vagrantfile
        vagrantfile_path = os.path.join(vm_dir, 'Vagrantfile')
        with open(vagrantfile_path, 'w') as f:
            f.write(content)

        return vagrantfile_path
