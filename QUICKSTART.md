# HAA-Gaia Quick Start Guide

This guide will help you get HAA-Gaia up and running in minutes.

## Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)
- Access to a Proxmox VE instance (for MVP testing)

## Quick Start with Docker

The fastest way to get started is using Docker Compose:

```bash
# 1. Clone the repository
git clone https://github.com/Rayleeigh/HAA-Gaia.git
cd HAA-Gaia

# 2. Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env and add your Proxmox credentials

# 3. Start all services
docker-compose up -d

# 4. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Configuration

Edit `backend/.env` with your settings:

```env
# Proxmox Configuration
PROXMOX_HOST=your-proxmox-host.com
PROXMOX_USER=root@pam
PROXMOX_PASSWORD=your-password
PROXMOX_VERIFY_SSL=false

# Database (default should work)
DATABASE_URL=postgresql://gaia:gaia_dev_password@postgres:5432/gaia_db

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=change-this-to-a-random-string
```

## Local Development Setup

If you prefer to run services locally without Docker:

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL and Redis (via Docker)
docker-compose up -d postgres redis

# Run database migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload

# Start Celery worker (in another terminal)
celery -A app.tasks.celery_app worker --loglevel=info
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## First Steps

1. **Check Providers**: Navigate to the Providers page to verify Proxmox connection
2. **Create a Template**: Go to Templates and create your first VM template
3. **Launch a VM**: Use the Create VM page to spin up your first virtual machine
4. **Monitor**: Watch your VMs on the Dashboard and VM List pages

## Testing the API

You can test the API directly using the interactive docs:

```
http://localhost:8000/docs
```

Example API calls:

```bash
# List providers
curl http://localhost:8000/api/v1/providers

# Create a VM
curl -X POST http://localhost:8000/api/v1/vms \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-vm",
    "provider": "proxmox",
    "config": {
      "box": "generic/ubuntu2204",
      "cpus": 2,
      "memory": 2048,
      "provider_config": {
        "node": "pve",
        "storage": "local-lvm",
        "disk_size": "32G"
      }
    }
  }'

# List VMs
curl http://localhost:8000/api/v1/vms

# Generate a Vagrantfile
curl -X POST http://localhost:8000/api/v1/vagrantfiles/generate \
  -H "Content-Type: application/json" \
  -d '{
    "box": "generic/ubuntu2204",
    "provider": "proxmox",
    "cpus": 2,
    "memory": 2048
  }'
```

## Common Issues

### Cannot connect to Proxmox

- Verify your Proxmox host is accessible
- Check credentials in `.env`
- Ensure firewall allows connections to Proxmox API (port 8006)
- Try setting `PROXMOX_VERIFY_SSL=false` for self-signed certificates

### Database errors

- Ensure PostgreSQL is running: `docker-compose ps postgres`
- Check database URL in `.env`
- Try recreating the database: `docker-compose down -v && docker-compose up -d`

### Frontend can't reach backend

- Verify backend is running on port 8000
- Check CORS settings in `backend/app/core/config.py`
- Ensure `VITE_API_URL` in frontend matches your backend URL

## Next Steps

- Read the full [README.md](README.md) for detailed architecture information
- Check [CONTRIBUTING.md](CONTRIBUTING.md) to learn how to add new providers
- Explore the template examples in the `templates/` directory
- Join the community and share your feedback!

## Getting Help

- 📖 [Full Documentation](README.md)
- 🐛 [Report Issues](https://github.com/Rayleeigh/HAA-Gaia/issues)
- 💬 [Discussions](https://github.com/Rayleeigh/HAA-Gaia/discussions)

Happy orchestrating! 🚀
