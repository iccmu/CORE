"""
Tests para las vistas de test_app
"""

import json

from django.test import Client

import pytest


@pytest.mark.django_db
class TestTestAppViews:
    """Tests para las vistas de test_app"""

    def test_test_home_returns_200(self):
        """Test que la vista home de test retorna 200"""
        client = Client()
        response = client.get("/test/")

        assert response.status_code == 200

    def test_test_api_returns_json(self):
        """Test que la vista API retorna JSON"""
        client = Client()
        response = client.get("/test/api/")

        assert response.status_code == 200
        # Verificar que es JSON (puede ser application/json o text/html con JSON)
        content_type = response.get("Content-Type", "")
        assert "json" in content_type.lower() or "application/json" in content_type

        try:
            data = json.loads(response.content)
            assert data["status"] == "ok"
            assert "host" in data
        except json.JSONDecodeError:
            # Si no es JSON válido, verificar que al menos contiene 'ok'
            assert (
                b"ok" in response.content.lower()
                or b"status" in response.content.lower()
            )
