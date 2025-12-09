"""
Pytest configuration and shared fixtures
"""
import pytest
from django.test import RequestFactory
from django.conf import settings

# Configurar settings para tests
@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Configuración de base de datos para tests"""
    with django_db_blocker.unblock():
        # Asegurar que DATABASES tiene la estructura correcta
        if 'default' not in settings.DATABASES:
            settings.DATABASES['default'] = {}
        
        # Usar SQLite en memoria para tests
        settings.DATABASES['default'].update({
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        })
        
        # Añadir ATOMIC_REQUESTS si no está presente
        if 'ATOMIC_REQUESTS' not in settings.DATABASES['default']:
            settings.DATABASES['default']['ATOMIC_REQUESTS'] = False

@pytest.fixture
def factory():
    """RequestFactory para crear requests en tests"""
    return RequestFactory()

@pytest.fixture
def user(django_user_model):
    """Fixture para crear un usuario de prueba"""
    return django_user_model.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def admin_user(django_user_model):
    """Fixture para crear un usuario administrador"""
    return django_user_model.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )

