"""
Tests para el middleware multi-dominio
"""

from django.conf import settings
from django.test import RequestFactory

import pytest

from proyectos.middleware import DomainUrlConfMiddleware


@pytest.mark.django_db
class TestDomainUrlConfMiddleware:
    """Tests para DomainUrlConfMiddleware"""

    def test_middleware_with_fondos_domain(self, factory):
        """Test que el middleware selecciona el URLConf correcto para fondos.iccmu.es"""
        request = factory.get("/", HTTP_HOST="fondos.iccmu.es")
        middleware = DomainUrlConfMiddleware(lambda req: None)

        middleware(request)

        assert request.urlconf == "proyectos.urls_fondos"

    def test_middleware_with_madmusic_domain(self, factory):
        """Test que el middleware selecciona el URLConf correcto para madmusic.iccmu.es"""
        request = factory.get("/", HTTP_HOST="madmusic.iccmu.es")
        middleware = DomainUrlConfMiddleware(lambda req: None)

        middleware(request)

        assert request.urlconf == "proyectos.urls_madmusic"

    def test_middleware_with_test_domain(self, factory):
        """Test que el middleware selecciona el URLConf correcto para test.iccmu.es"""
        request = factory.get("/", HTTP_HOST="test.iccmu.es")
        middleware = DomainUrlConfMiddleware(lambda req: None)

        middleware(request)

        assert request.urlconf == "proyectos.urls_test"

    def test_middleware_with_localhost(self, factory):
        """Test que el middleware usa el URLConf root para localhost"""
        request = factory.get("/", HTTP_HOST="localhost:8000")
        middleware = DomainUrlConfMiddleware(lambda req: None)

        middleware(request)

        assert request.urlconf == settings.ROOT_URLCONF

    def test_middleware_with_unknown_domain(self, factory):
        """Test que el middleware usa el URLConf root para dominios desconocidos"""
        # Añadir temporalmente el dominio a ALLOWED_HOSTS para el test
        original_allowed_hosts = settings.ALLOWED_HOSTS.copy()
        settings.ALLOWED_HOSTS.append("unknown.iccmu.es")

        try:
            request = factory.get("/", HTTP_HOST="unknown.iccmu.es")
            middleware = DomainUrlConfMiddleware(lambda req: None)

            middleware(request)

            assert request.urlconf == settings.ROOT_URLCONF
        finally:
            # Restaurar ALLOWED_HOSTS original
            settings.ALLOWED_HOSTS = original_allowed_hosts

    def test_middleware_strips_port(self, factory):
        """Test que el middleware maneja correctamente los puertos en el host"""
        request = factory.get("/", HTTP_HOST="fondos.iccmu.es:8000")
        middleware = DomainUrlConfMiddleware(lambda req: None)

        middleware(request)

        assert request.urlconf == "proyectos.urls_fondos"
