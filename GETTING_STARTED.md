# Getting Started with HAA-Gaia

This guide will walk you through setting up HAA-Gaia and creating your first virtual machine.

## Quick Start Options

Choose the setup method that best fits your needs:

### Option 1: Docker Compose (Recommended)
Best for: Quick testing and development

### Option 2: Local Development
Best for: Active development and debugging

### Option 3: Production Deployment
Best for: Production environments

---

## Option 1: Docker Compose Setup

### Prerequisites
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose
- At least one virtualization provider installed

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Rayleeigh/HAA-Gaia.git
   cd HAA-Gaia
   ```

2. **Configure environment**
   ```bash
   cp backend/.env.example backend/.env
   ```

   Edit `backend/.env` and configure your providers:
   ```env
   # Proxmox (if using)
   PROXMOX_HOST=your-proxmox-host.com
   PROXMOX_USER=root@pam
   PROXMOX_PASSWORD=your-password

   # Other settings
   SECRET_KEY=change-this-to-random-string
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

5. **Verify providers**
   - Navigate to Providers page in the UI
   - Check which providers are available on your system

---

## Option 2: Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL
- Redis
- At least one virtualization provider

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# Start database and redis
docker-compose up -d postgres redis

# Run backend
uvicorn app.main:app --reload

# In another terminal, start Celery worker
celery -A app.tasks.celery_app worker --loglevel=info
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

---

## Provider Setup

HAA-Gaia works with different virtualization providers. Set up the ones you need:

### VirtualBox Setup

**Windows:**
```powershell
# Using Chocolatey
choco install virtualbox

# Or download from: https://www.virtualbox.org/
```

**Mac:**
```bash
brew install --cask virtualbox
```

**Linux:**
```bash
sudo apt-get install virtualbox
```

**Verify Installation:**
```bash
VBoxManage --version
```

### Hyper-V Setup (Windows Only)

**Enable Hyper-V:**
```powershell
# Windows 10/11 Pro/Enterprise
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

# Or via PowerShell (requires restart)
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All
```

**Verify Installation:**
```powershell
Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V
Get-VM
```

**Note:** Hyper-V and VirtualBox cannot run simultaneously. Choose one.

### WSL2 Setup (Windows Only)

**Install WSL:**
```powershell
wsl --install
```

**Set WSL2 as default:**
```powershell
wsl --set-default-version 2
```

**Install a distribution:**
```powershell
wsl --install -d Ubuntu-22.04
```

**Verify Installation:**
```powershell
wsl --status
wsl --list --verbose
```

### Proxmox Setup

Proxmox runs on a dedicated server. Configure connection in `.env`:

```env
PROXMOX_HOST=192.168.1.100
PROXMOX_USER=root@pam
PROXMOX_PASSWORD=your-password
PROXMOX_VERIFY_SSL=false
```

**Test Connection:**
```bash
curl -k https://PROXMOX_HOST:8006/api2/json/access/ticket \
  -d "username=root@pam" \
  -d "password=your-password"
```

---

## Creating Your First VM

### Via Web UI

1. **Navigate to Dashboard**
   - Open http://localhost:3000
   - Check provider status on Providers page

2. **Create New VM**
   - Click "Create VM" or go to VMs → Create
   - Fill in the form:
     - **Name:** my-first-vm
     - **Provider:** Choose VirtualBox (easiest for testing)
     - **CPUs:** 2
     - **Memory:** 2048 MB
   - Click "Create VM"

3. **Monitor Creation**
   - VM will be created asynchronously
   - Check status on VM List page
   - Wait for state to change from "creating" to "stopped"

4. **Start VM**
   - Click the Start button
   - VM will boot up
   - Status will change to "running"

### Via API

**Create VM with VirtualBox:**
```bash
curl -X POST http://localhost:8000/api/v1/vms \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ubuntu-dev",
    "provider": "virtualbox",
    "description": "Ubuntu development environment",
    "config": {
      "box": "bento/ubuntu-22.04",
      "cpus": 2,
      "memory": 4096,
      "disk_size": 32768,
      "provider_config": {
        "gui": false
      }
    }
  }'
```

**Check VM Status:**
```bash
curl http://localhost:8000/api/v1/vms
```

**Start VM:**
```bash
curl -X POST http://localhost:8000/api/v1/vms/1/start
```

---

## Using Templates

### Browse Templates

1. Navigate to Templates page
2. View available templates for different providers
3. Click "Use Template" to create VM from template

### Import Vagrantfile

1. Go to Templates → Import
2. Upload your existing Vagrantfile
3. Template will be created automatically

### Create Custom Template

```bash
curl -X POST http://localhost:8000/api/v1/templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Custom Template",
    "provider": "virtualbox",
    "description": "Custom Ubuntu setup",
    "config": {
      "box": "bento/ubuntu-22.04",
      "cpus": 2,
      "memory": 4096,
      "provisioners": [
        {
          "type": "shell",
          "inline": [
            "apt-get update",
            "apt-get install -y docker.io"
          ]
        }
      ]
    },
    "tags": ["ubuntu", "docker"]
  }'
```

---

## Common Workflows

### Development Environment

1. **Create WSL Distribution** (Windows)
   ```json
   {
     "name": "Dev-Environment",
     "provider": "wsl",
     "config": {
       "source_distro": "Ubuntu-22.04",
       "default_user": "developer",
       "provisioners": [{
         "type": "shell",
         "inline": [
           "apt-get update",
           "apt-get install -y git nodejs npm docker.io"
         ]
       }]
     }
   }
   ```

2. **Create VirtualBox VM** (Cross-platform)
   - Use template: `virtualbox-ubuntu.yaml`
   - Adjust resources as needed
   - Enable shared folders for project access

### Testing Environment

1. **Create Multiple VMs**
   - Use Hyper-V or VirtualBox
   - Create network configuration
   - Use linked clones for faster creation

2. **Use Snapshots**
   - Create baseline snapshot
   - Test changes
   - Revert if needed

### Production Staging

1. **Use Proxmox**
   - Create VMs matching production
   - Test deployments
   - Validate configurations

---

## Troubleshooting

### Backend Won't Start

**Check PostgreSQL:**
```bash
docker-compose ps postgres
docker-compose logs postgres
```

**Check Redis:**
```bash
docker-compose ps redis
```

**Check Python environment:**
```bash
python --version
pip list
```

### Provider Not Available

**VirtualBox:**
```bash
# Check installation
VBoxManage --version

# Check PATH
which VBoxManage  # Mac/Linux
where VBoxManage  # Windows
```

**Hyper-V:**
```powershell
# Check if enabled
Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V

# Check permissions
Get-VM  # Should run without error
```

**WSL:**
```powershell
wsl --status
wsl --list --verbose
```

### VM Creation Fails

1. **Check Celery worker:**
   ```bash
   celery -A app.tasks.celery_app worker --loglevel=debug
   ```

2. **Check provider logs:**
   - Backend logs: `docker-compose logs backend`
   - Celery logs: `docker-compose logs celery-worker`

3. **Check resources:**
   - Sufficient disk space
   - Enough RAM
   - CPU virtualization enabled in BIOS

### Frontend Can't Connect

1. **Check backend status:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check CORS settings:**
   - Verify `CORS_ORIGINS` in `backend/app/core/config.py`

3. **Check proxy configuration:**
   - Review `frontend/vite.config.js`

---

## Next Steps

1. **Explore Templates**
   - Check `templates/` directory
   - Create your own templates
   - Share with team

2. **Read Provider Documentation**
   - See [PROVIDERS.md](PROVIDERS.md)
   - Learn provider-specific features
   - Optimize configurations

3. **Set Up CI/CD**
   - Automate VM creation
   - Use templates in pipelines
   - Integrate with existing tools

4. **Advanced Features**
   - Multi-VM orchestration
   - Custom provisioning scripts
   - Network configuration

---

## Useful Commands

### Docker Management
```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart services
docker-compose restart backend
docker-compose restart celery-worker

# Reset everything
docker-compose down -v
docker-compose up -d
```

### Database Management
```bash
# Access database
docker-compose exec postgres psql -U gaia -d gaia_db

# View tables
\dt

# Query VMs
SELECT * FROM virtual_machines;
```

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# List providers
curl http://localhost:8000/api/v1/providers

# List VMs
curl http://localhost:8000/api/v1/vms

# Generate Vagrantfile
curl -X POST http://localhost:8000/api/v1/vagrantfiles/generate \
  -H "Content-Type: application/json" \
  -d '{"box": "ubuntu/focal64", "cpus": 2, "memory": 2048}'
```

---

## Getting Help

- **Documentation:** [README.md](README.md), [PROVIDERS.md](PROVIDERS.md)
- **Issues:** https://github.com/Rayleeigh/HAA-Gaia/issues
- **Discussions:** https://github.com/Rayleeigh/HAA-Gaia/discussions

Happy virtualizing! 🚀
