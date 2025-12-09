# 🧪 Testing Rápido

## Ejecutar Tests

```bash
# Todos los tests
pytest

# Con coverage
pytest --cov=. --cov-report=html

# Tests específicos
pytest tests/core/
```

## Verificar Código

```bash
# Formatear
black .
isort .

# Linting
flake8 .
pylint proyectos/

# Seguridad
bandit -r .
safety check
```

## CI/CD

Los tests se ejecutan automáticamente en cada push a través de GitHub Actions.

Ver `TESTING.md` para documentación completa.

