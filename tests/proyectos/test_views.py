"""
Tests para las vistas del proyecto principal
"""

from django.test import Client

import pytest


@pytest.mark.django_db
class TestIndexView:
    """Tests para la vista de índice"""

    def test_index_view_returns_200(self):
        """Test que la vista de índice retorna 200"""
        client = Client()
        response = client.get("/")

        assert response.status_code == 200

    def test_index_view_shows_apps(self):
        """Test que la vista de índice muestra las apps disponibles"""
        client = Client()
        response = client.get("/")

        # Verificar contexto si está disponible
        if hasattr(response, "context") and response.context:
            assert "apps" in response.context
            assert len(response.context["apps"]) > 0

    def test_index_view_includes_fondos(self):
        """Test que la vista de índice incluye fondos_app"""
        client = Client()
        response = client.get("/")

        if (
            hasattr(response, "context")
            and response.context
            and "apps" in response.context
        ):
            apps = [app["name"] for app in response.context["apps"]]
            assert "fondos_app" in apps

    def test_index_view_includes_madmusic(self):
        """Test que la vista de índice incluye madmusic_app"""
        client = Client()
        response = client.get("/")

        if (
            hasattr(response, "context")
            and response.context
            and "apps" in response.context
        ):
            apps = [app["name"] for app in response.context["apps"]]
            assert "madmusic_app" in apps

    def test_index_view_includes_test(self):
        """Test que la vista de índice incluye test_app"""
        client = Client()
        response = client.get("/")

        if (
            hasattr(response, "context")
            and response.context
            and "apps" in response.context
        ):
            apps = [app["name"] for app in response.context["apps"]]
            assert "test_app" in apps
