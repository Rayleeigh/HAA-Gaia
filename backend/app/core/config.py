from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "HAA-Gaia"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://gaia:gaia_dev_password@localhost:5432/gaia_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Proxmox (MVP Provider)
    PROXMOX_HOST: str = ""
    PROXMOX_USER: str = "root@pam"
    PROXMOX_PASSWORD: str = ""
    PROXMOX_VERIFY_SSL: bool = False

    # Paths
    TEMPLATES_DIR: str = os.path.join(os.path.dirname(__file__), "../../../templates")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
