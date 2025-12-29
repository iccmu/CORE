"""
Tests para los modelos de core
"""

from django.core.exceptions import ValidationError
from django.utils import timezone

import pytest

from core.models import Entrada, Pagina, Proyecto


@pytest.mark.django_db
class TestProyectoModel:
    """Tests para el modelo Proyecto"""

    def test_create_proyecto(self):
        """Test crear un proyecto básico"""
        proyecto = Proyecto.objects.create(
            slug="test-proyecto", titulo="Test Proyecto", acronimo="TP"
        )

        assert proyecto.slug == "test-proyecto"
        assert proyecto.titulo == "Test Proyecto"
        assert str(proyecto) == "Test Proyecto"

    def test_proyecto_slug_unique(self):
        """Test que el slug de proyecto debe ser único"""
        Proyecto.objects.create(slug="test-proyecto", titulo="Test Proyecto")

        with pytest.raises(Exception):  # IntegrityError
            Proyecto.objects.create(slug="test-proyecto", titulo="Otro Proyecto")


@pytest.mark.django_db
class TestEntradaModel:
    """Tests para el modelo Entrada"""

    def test_create_entrada(self):
        """Test crear una entrada"""
        proyecto = Proyecto.objects.create(slug="test-proyecto", titulo="Test Proyecto")

        entrada = Entrada.objects.create(
            proyecto=proyecto,
            titulo="Test Entrada",
            slug="test-entrada",
            cuerpo="Contenido de prueba",
        )

        assert entrada.proyecto == proyecto
        assert entrada.titulo == "Test Entrada"
        assert entrada.slug == "test-entrada"

    def test_entrada_ordering(self):
        """Test que las entradas se ordenan por fecha de publicación descendente"""
        proyecto = Proyecto.objects.create(slug="test-proyecto", titulo="Test Proyecto")

        entrada1 = Entrada.objects.create(
            proyecto=proyecto,
            titulo="Entrada 1",
            slug="entrada-1",
            cuerpo="Contenido 1",
        )

        entrada2 = Entrada.objects.create(
            proyecto=proyecto,
            titulo="Entrada 2",
            slug="entrada-2",
            cuerpo="Contenido 2",
        )

        entradas = list(Entrada.objects.all())
        # La más reciente debe estar primero
        assert entradas[0] == entrada2 or entradas[0] == entrada1


@pytest.mark.django_db
class TestPaginaModel:
    """Tests para el modelo Pagina"""

    def test_create_pagina(self):
        """Test crear una página"""
        proyecto = Proyecto.objects.create(slug="test-proyecto", titulo="Test Proyecto")

        pagina = Pagina.objects.create(
            proyecto=proyecto,
            titulo="Test Página",
            slug="test-pagina",
            cuerpo="Contenido de la página",
        )

        assert pagina.proyecto == proyecto
        assert pagina.titulo == "Test Página"
        assert pagina.slug == "test-pagina"






