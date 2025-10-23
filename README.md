# HAA-Gaia

**Modular Virtualization Orchestration Suite**

A Portainer-like web UI for managing virtualized environments across multiple platforms (Proxmox, VirtualBox, Hyper-V, WSL) through a unified Vagrant-based abstraction layer.

## Vision

HAA-Gaia simplifies VM lifecycle management by providing:
- **Unified Interface**: Web-based UI for managing VMs across different virtualization platforms
- **Vagrant Generation**: Create, parse, and template Vagrantfiles without requiring Vagrant installation
- **Modular Providers**: Plugin-based architecture supporting multiple backends
- **Async Operations**: Non-blocking VM provisioning and management
- **Template Library**: Reusable environment configurations

## Architecture

```
┌─────────────────────────────────────────┐
│         Web UI (React/Vue)              │
│  ┌───────────┐ ┌──────────┐ ┌─────────┐│
│  │ Dashboard │ │ VM Panel │ │Templates││
│  └───────────┘ └──────────┘ └─────────┘│
└─────────────────┬───────────────────────┘
                  │ REST API
┌─────────────────▼───────────────────────┐
│      FastAPI Backend (Python)           │
│  ┌──────────────────────────────────┐   │
│  │   Vagrantfile Engine              │   │
│  │  ├─ Parser                        │   │
│  │  ├─ Generator                     │   │
│  │  └─ Template Manager              │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │   Provider Abstraction Layer     │   │
│  │  ├─ Proxmox ✅                   │   │
│  │  ├─ VirtualBox ✅                │   │
│  │  ├─ Hyper-V ✅                   │   │
│  │  └─ WSL2 ✅                      │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │   Async Task Queue (Celery)      │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
    PostgreSQL          Redis
   (Metadata)         (Queue/Cache)
```

## Tech Stack

### Backend
- **FastAPI**: Async Python web framework
- **SQLAlchemy**: ORM for database operations
- **Celery**: Distributed task queue
- **Redis**: Message broker and caching
- **Python-vagrant**: Vagrantfile parsing
- **Jinja2**: Template rendering

### Frontend
- **React** (or Vue.js): UI framework
- **WebSocket**: Real-time updates
- **Axios**: API client
- **Monaco Editor**: Code editor for Vagrantfiles

### Infrastructure
- **Docker & Docker Compose**: Containerized deployment
- **PostgreSQL**: Persistent storage

## Implemented Features

### Core Features
- ✅ Vagrantfile parser
- ✅ Vagrantfile generator from UI forms
- ✅ Template management (save, load, share)
- ✅ Async VM provisioning with Celery
- ✅ VM lifecycle management (create, start, stop, destroy)
- ✅ Real-time operation logs
- ✅ Multi-provider support

### Supported Providers
- ✅ **Proxmox VE** - Enterprise virtualization platform
- ✅ **VirtualBox** - Cross-platform desktop virtualization
- ✅ **Hyper-V** - Windows native hypervisor
- ✅ **WSL2** - Windows Subsystem for Linux

See [PROVIDERS.md](PROVIDERS.md) for detailed provider documentation.

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Proxmox VE instance (for MVP testing)

### Development Setup

```bash
# Clone repository
git clone https://github.com/Rayleeigh/HAA-Gaia.git
cd HAA-Gaia

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Start development environment
docker-compose up -d  # Starts PostgreSQL, Redis
cd ../backend && uvicorn app.main:app --reload
cd ../frontend && npm run dev
```

## Project Structure

```
HAA-Gaia/
├── backend/
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── core/             # Core configuration
│   │   ├── models/           # Database models
│   │   ├── services/         # Business logic
│   │   │   ├── vagrant/      # Vagrant operations
│   │   │   └── providers/    # Provider implementations
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── tasks/            # Celery tasks
│   │   └── main.py           # Application entry point
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API clients
│   │   └── App.jsx
│   └── package.json
├── templates/                # Vagrantfile templates
├── docker-compose.yml
└── README.md
```

## Roadmap

### Phase 1: MVP (Proxmox)
- Core Vagrantfile engine
- Proxmox provider
- Basic web UI
- Template system

### Phase 2: Additional Providers & Features
- VMware integration
- Additional cloud providers (AWS, Azure, GCP)

### Phase 3: Advanced Features
- Multi-VM orchestration
- Network topology designer
- Resource monitoring
- Team collaboration features
- Template marketplace

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## License

MIT License - See LICENSE file for details

## Acknowledgments

Inspired by Portainer's approach to container management, applied to the virtualization domain.
