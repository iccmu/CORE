# Testing y CI/CD - Guía Completa

## 🎯 Sistema de Testing Automatizado

Hemos configurado un sistema completo de testing automatizado que se ejecuta en cada push al repositorio.

## 📋 Estructura de Tests

```
tests/
├── conftest.py              # Configuración y fixtures compartidas
├── core/
│   └── test_models.py      # Tests de modelos core
├── fondos_app/
│   └── test_views.py       # Tests de vistas fondos
├── madmusic_app/
│   └── test_views.py       # Tests de vistas madmusic
├── proyectos/
│   ├── test_middleware.py  # Tests del middleware multi-dominio
│   └── test_views.py       # Tests de vistas principales
└── test_app/
    └── test_test_views.py  # Tests de app de pruebas
```

## 🚀 Comandos de Testing

### Ejecutar todos los tests
```bash
pytest
```

### Ejecutar tests con coverage
```bash
pytest --cov=. --cov-report=html
```

### Ejecutar tests específicos
```bash
pytest tests/core/
pytest tests/proyectos/test_middleware.py
pytest tests/fondos_app/test_views.py::TestFondosViews::test_fondos_home_returns_200
```

### Ejecutar tests en paralelo (si tienes pytest-xdist)
```bash
pytest -n auto
```

### Ver coverage report
```bash
# Después de ejecutar con --cov-report=html
open htmlcov/index.html
```

## 🔧 Herramientas de Calidad de Código

### Linting
```bash
# Flake8
flake8 .

# Pylint
pylint proyectos/ core/ fondos_app/ madmusic_app/ test_app/

# MyPy (type checking)
mypy . --ignore-missing-imports
```

### Formateo
```bash
# Formatear código
black .
isort .

# Verificar formato sin cambiar
black --check .
isort --check-only .
```

### Seguridad
```bash
# Bandit (security linting)
bandit -r . -f json

# Safety (vulnerabilidades en dependencias)
safety check
```

## 📊 CI/CD Pipeline

### GitHub Actions Workflows

#### 1. CI Pipeline (`.github/workflows/ci.yml`)

Se ejecuta en cada push y PR, incluye:

- **Tests**: Ejecuta todos los tests en Python 3.11 y 3.12
- **Linting**: Flake8, Black, isort, Pylint, MyPy
- **Security**: Bandit y Safety
- **Django Checks**: Verifica configuración de Django
- **Coverage**: Sube reportes a Codecov

#### 2. Pre-commit Checks (`.github/workflows/pre-commit.yml`)

Se ejecuta en PRs, verifica:
- Formato de código (Black, isort)
- Linting básico (Flake8)

### Estado del Pipeline

El pipeline verifica:
- ✅ Tests pasan
- ✅ Código formateado correctamente
- ✅ Sin errores de linting críticos
- ✅ Sin vulnerabilidades de seguridad conocidas
- ✅ Configuración de Django correcta

## 📈 Coverage

**Objetivo mínimo:** 70% de cobertura de código

El coverage se calcula automáticamente y se muestra en:
- Terminal durante ejecución de tests
- Reporte HTML en `htmlcov/index.html`
- Codecov (si está configurado)

## 🧪 Escribir Nuevos Tests

### Estructura de un Test

```python
import pytest
from django.test import Client

@pytest.mark.django_db
class TestMiVista:
    """Tests para mi vista"""
    
    def test_vista_retorna_200(self):
        """Test que la vista retorna 200"""
        client = Client()
        response = client.get('/mi-ruta/')
        
        assert response.status_code == 200
    
    def test_vista_usa_template_correcto(self):
        """Test que la vista usa el template correcto"""
        client = Client()
        response = client.get('/mi-ruta/')
        
        assert 'mi_template.html' in [t.name for t in response.templates]
```

### Fixtures Disponibles

- `factory`: RequestFactory para crear requests
- `user`: Usuario de prueba
- `admin_user`: Usuario administrador

### Marcadores de Tests

- `@pytest.mark.django_db`: Requiere acceso a base de datos
- `@pytest.mark.slow`: Tests lentos (ejecutar con `-m "not slow"`)
- `@pytest.mark.integration`: Tests de integración
- `@pytest.mark.unit`: Tests unitarios

## 🔍 Análisis Automático

### En cada Push

1. **Tests automáticos**: Se ejecutan todos los tests
2. **Análisis de código**: Linting y type checking
3. **Análisis de seguridad**: Bandit y Safety
4. **Coverage**: Se calcula y reporta automáticamente

### Reportes Generados

- Coverage report (HTML)
- Security reports (JSON)
- Test results (en GitHub Actions)

## 📝 Makefile

Comandos útiles disponibles:

```bash
make test              # Ejecutar todos los tests
make test-coverage     # Tests con coverage
make lint              # Ejecutar linters
make format            # Formatear código
make format-check      # Verificar formato sin cambiar
make security          # Verificar seguridad
make check             # Django checks
make clean             # Limpiar archivos temporales
```

## ✅ Checklist antes de Push

- [ ] Tests pasan localmente (`pytest`)
- [ ] Coverage > 70% (`pytest --cov=.`)
- [ ] Código formateado (`black .` y `isort .`)
- [ ] Sin errores de linting (`flake8 .`)
- [ ] Django checks pasan (`python manage.py check`)
- [ ] Sin vulnerabilidades (`safety check`)

## 🐛 Troubleshooting

### Tests fallan localmente pero pasan en CI
- Verificar que tienes las mismas versiones de dependencias
- Limpiar cache: `make clean`

### Coverage bajo
- Añadir más tests para código no cubierto
- Revisar `htmlcov/index.html` para ver qué falta

### Linting errors
- Ejecutar `black .` y `isort .` para formatear automáticamente
- Revisar errores de Pylint y corregir manualmente

## 📚 Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-django](https://pytest-django.readthedocs.io/)
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Coverage.py](https://coverage.readthedocs.io/)








