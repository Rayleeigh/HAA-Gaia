from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from typing import Dict, Any

from app.schemas.vagrant import VagrantfileConfig
from app.services.vagrant.generator import VagrantfileGenerator
from app.services.vagrant.parser import VagrantfileParser

router = APIRouter()


@router.post("/generate", response_class=PlainTextResponse)
async def generate_vagrantfile(config: VagrantfileConfig):
    """Generate a Vagrantfile from configuration"""
    try:
        generator = VagrantfileGenerator()
        vagrantfile_content = generator.generate(config.dict())
        return vagrantfile_content
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate Vagrantfile: {str(e)}")


@router.post("/parse")
async def parse_vagrantfile(vagrantfile: str) -> Dict[str, Any]:
    """Parse an existing Vagrantfile and extract configuration"""
    try:
        parser = VagrantfileParser()
        config = parser.parse(vagrantfile)
        return config
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse Vagrantfile: {str(e)}")


@router.post("/validate")
async def validate_vagrantfile(vagrantfile: str) -> Dict[str, Any]:
    """Validate a Vagrantfile syntax"""
    try:
        parser = VagrantfileParser()
        is_valid = parser.validate(vagrantfile)
        return {
            "valid": is_valid,
            "message": "Vagrantfile is valid" if is_valid else "Vagrantfile has syntax errors"
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"Validation error: {str(e)}"
        }
