"""
Tests para las vistas de madmusic_app
"""

from django.test import Client

import pytest


@pytest.mark.django_db
class TestMadmusicViews:
    """Tests para las vistas de madmusic_app"""

    def test_madmusic_home_returns_200(self):
        """Test que la vista home de madmusic retorna 200"""
        client = Client()
        response = client.get("/madmusic/")

        assert response.status_code == 200

    def test_madmusic_home_uses_template(self):
        """Test que la vista home usa el template correcto"""
        client = Client()
        response = client.get("/madmusic/")

        # Verificar que el template se usó
        template_names = [t.name for t in response.templates if hasattr(t, "name")]
        assert "madmusic/home.html" in template_names or any(
            "madmusic/home" in str(t) for t in response.templates
        )
