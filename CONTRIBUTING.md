# Contributing to HAA-Gaia

Thank you for your interest in contributing to HAA-Gaia! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature/fix
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

See the [README.md](README.md) for development setup instructions.

## Adding New Providers

To add support for a new virtualization provider:

1. Create a new provider class in `backend/app/services/providers/`
2. Inherit from `BaseProvider` and implement all abstract methods
3. Register the provider using the `@ProviderRegistry.register` decorator
4. Add provider-specific Vagrantfile templates if needed
5. Update documentation

Example:

```python
from app.services.providers.base import BaseProvider, ProviderRegistry
from app.schemas.provider import ProviderType

@ProviderRegistry.register
class MyProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "myprovider"

    @property
    def display_name(self) -> str:
        return "My Provider"

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.MYPROVIDER

    # Implement other required methods...
```

## Code Style

### Python
- Follow PEP 8 guidelines
- Use type hints where applicable
- Run `black` for formatting
- Run `flake8` for linting

### JavaScript/React
- Use ESLint configuration provided
- Follow React best practices
- Use functional components with hooks

## Testing

- Write unit tests for new features
- Ensure all tests pass before submitting PR
- Add integration tests for provider implementations

## Pull Request Process

1. Update documentation for any new features
2. Add tests for your changes
3. Ensure all tests pass
4. Update CHANGELOG.md with your changes
5. Submit PR with clear description of changes

## Code of Conduct

Be respectful and inclusive. We're all here to build something great together.

## Questions?

Open an issue for questions or join our discussions.
