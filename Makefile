.PHONY: help test lint format security install dev-install clean

help:
	@echo "Comandos disponibles:"
	@echo "  make install          - Instalar dependencias de producción"
	@echo "  make dev-install      - Instalar dependencias de desarrollo"
	@echo "  make test             - Ejecutar todos los tests"
	@echo "  make test-coverage    - Ejecutar tests con coverage"
	@echo "  make lint             - Ejecutar linters (flake8, pylint)"
	@echo "  make format           - Formatear código (black, isort)"
	@echo "  make security         - Verificar seguridad (bandit, safety)"
	@echo "  make check            - Ejecutar Django checks"
	@echo "  make clean            - Limpiar archivos temporales"

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	pytest

test-coverage:
	pytest --cov=. --cov-report=html --cov-report=term-missing

lint:
	flake8 .
	pylint proyectos/ core/ fondos_app/ madmusic_app/ test_app/
	mypy . --ignore-missing-imports || true

format:
	black .
	isort .

format-check:
	black --check .
	isort --check-only .

security:
	bandit -r . -f json
	safety check

check:
	python manage.py check
	python manage.py check --deploy

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/








