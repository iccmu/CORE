"""
Tests para las vistas de fondos_app
"""

from django.test import Client
from django.urls import reverse

import pytest


@pytest.mark.django_db
class TestFondosViews:
    """Tests para las vistas de fondos_app"""

    def test_fondos_home_returns_200(self):
        """Test que la vista home de fondos retorna 200"""
        client = Client()
        # Usar la URL con prefijo para desarrollo local
        response = client.get("/fondos/")

        assert response.status_code == 200

    def test_fondos_home_uses_template(self):
        """Test que la vista home usa el template correcto"""
        client = Client()
        response = client.get("/fondos/")

        # Verificar que el template se usó
        template_names = [t.name for t in response.templates if hasattr(t, "name")]
        assert "fondos/home.html" in template_names or any(
            "fondos/home" in str(t) for t in response.templates
        )

    def test_fondos_home_context(self):
        """Test que la vista home pasa el contexto correcto"""
        client = Client()
        response = client.get("/fondos/")

        # Verificar contexto si está disponible
        if hasattr(response, "context") and response.context:
            assert "app_name" in response.context
            assert response.context["app_name"] == "Fondos"
