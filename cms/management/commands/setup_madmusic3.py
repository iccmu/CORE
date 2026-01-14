"""
Comando para crear la estructura inicial de Madmusic3 con páginas vacías.

Uso:
    python manage.py setup_madmusic3
"""

import os
import yaml
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from wagtail.models import Site, Page
from cms.models import HomePage, StandardPage, NewsIndexPage


class Command(BaseCommand):
    help = "Crea la estructura inicial de Madmusic3 con páginas vacías basadas en menus_madmusic.yml"

    def handle(self, *args, **options):
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("CONFIGURANDO MADMUSIC3")
        self.stdout.write("=" * 80 + "\n")

        # 1. Obtener el root page de Wagtail
        wagtail_root = Page.objects.filter(depth=1).first()
        if not wagtail_root:
            self.stdout.write(
                self.style.ERROR("⚠ No se encontró el root page de Wagtail")
            )
            return

        # 2. Crear HomePage para madmusic3
        self.stdout.write("\n=== CREANDO HOMEPAGE ===")
        home_page = HomePage.objects.child_of(wagtail_root).filter(slug="madmusic3-home").first()
        
        if not home_page:
            home_page = HomePage(
                title="Madmusic3 Home",
                slug="madmusic3-home",
                intro="Bienvenido a Madmusic3",
            )
            wagtail_root.add_child(instance=home_page)
            home_page.save_revision().publish()
            self.stdout.write(
                self.style.SUCCESS("✓ HomePage 'Madmusic3 Home' creada")
            )
        else:
            self.stdout.write(f"✓ HomePage existente: {home_page.title}")

        # 3. Crear Sites de Wagtail
        self.stdout.write("\n=== CONFIGURANDO SITES DE WAGTAIL ===")
        
        # Site para producción (madmusic3.iccmu.es)
        site_prod, created = Site.objects.get_or_create(
            hostname="madmusic3.iccmu.es",
            port=80,
            defaults={
                "site_name": "Madmusic3",
                "root_page": home_page,
            },
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS("✓ Site creado: madmusic3.iccmu.es")
            )
        else:
            if site_prod.root_page != home_page:
                site_prod.root_page = home_page
                site_prod.save()
                self.stdout.write("✓ Site actualizado: madmusic3.iccmu.es")
            else:
                self.stdout.write("✓ Site existente: madmusic3.iccmu.es")

        # Site para desarrollo local (127.0.0.1:8000 con path /madmusic3/)
        # Nota: En localhost, el acceso será mediante /madmusic3/ en urls_root.py
        # que ya está configurado para usar wagtail_urls con el mismo Site
        self.stdout.write("✓ Acceso local configurado en urls_root.py: http://127.0.0.1:8000/madmusic3/")

        # 4. Leer y parsear menus_madmusic.yml
        self.stdout.write("\n=== CREANDO ESTRUCTURA DE PÁGINAS ===")
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        menu_file = os.path.join(base_dir, "menus_madmusic.yml")
        
        if not os.path.exists(menu_file):
            self.stdout.write(
                self.style.ERROR(f"⚠ No se encontró el archivo {menu_file}")
            )
            return

        # Leer el archivo
        with open(menu_file, 'r', encoding='utf-8') as f:
            menu_lines = f.readlines()

        # Parsear la estructura jerárquica basada en indentación
        pages_structure = self._parse_menu_structure(menu_lines)
        
        # Crear páginas
        self._create_pages(pages_structure, home_page)

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(
            self.style.SUCCESS("✓ Madmusic3 configurado exitosamente!")
        )
        self.stdout.write("\nAcceso:")
        self.stdout.write("  - Local: http://127.0.0.1:8000/madmusic3/")
        self.stdout.write("  - Admin: http://127.0.0.1:8000/madmusic3/admin/")
        self.stdout.write("  - Producción: http://madmusic3.iccmu.es/")
        self.stdout.write("  - Usuario: admin / admin123")
        self.stdout.write("=" * 80 + "\n")

    def _parse_menu_structure(self, menu_lines):
        """
        Parsea el archivo de menú y crea una estructura jerárquica.
        Retorna una lista de diccionarios con 'title', 'level' y 'children'.
        """
        structure = []
        stack = [{'level': -1, 'children': structure}]  # Stack para manejar jerarquía
        
        for line in menu_lines:
            # Determinar nivel de indentación (cada 4 espacios = 1 nivel)
            stripped = line.rstrip('\n')
            if not stripped.strip():
                continue
            
            indent = len(stripped) - len(stripped.lstrip(' '))
            level = indent // 4
            title = stripped.strip()
            
            # Crear nodo
            node = {
                'title': title,
                'level': level,
                'children': []
            }
            
            # Ajustar el stack al nivel correcto
            while stack[-1]['level'] >= level:
                stack.pop()
            
            # Agregar como hijo del padre actual
            stack[-1]['children'].append(node)
            
            # Agregar al stack para futuros hijos
            stack.append(node)
        
        return structure

    def _create_pages(self, structure, parent_page, created_pages=None):
        """
        Crea páginas recursivamente basándose en la estructura.
        """
        if created_pages is None:
            created_pages = set()
        
        for node in structure:
            title = node['title']
            slug = slugify(title)
            
            # Evitar duplicados en la misma sesión
            page_key = f"{parent_page.id}:{slug}"
            if page_key in created_pages:
                continue
            
            # Determinar tipo de página
            if title == "INICIO":
                # INICIO no se crea como página, es la HomePage
                self.stdout.write(f"  ✓ INICIO → HomePage existente")
                # Procesar hijos de INICIO como hijos de parent_page
                if node['children']:
                    self._create_pages(node['children'], parent_page, created_pages)
                continue
            elif title == "NOTICIAS":
                # Crear NewsIndexPage
                existing = NewsIndexPage.objects.child_of(parent_page).filter(slug=slug).first()
                if not existing:
                    page = NewsIndexPage(
                        title=title,
                        slug=slug,
                        intro="",
                    )
                    parent_page.add_child(instance=page)
                    page.save_revision().publish()
                    self.stdout.write(f"  ✓ Creada NewsIndexPage: {title}")
                else:
                    page = existing
                    self.stdout.write(f"  ✓ NewsIndexPage existente: {title}")
            else:
                # Crear StandardPage vacía
                existing = StandardPage.objects.child_of(parent_page).filter(slug=slug).first()
                if not existing:
                    page = StandardPage(
                        title=title,
                        slug=slug,
                        intro="",
                        body=[],  # StreamField vacío
                    )
                    parent_page.add_child(instance=page)
                    page.save_revision().publish()
                    self.stdout.write(f"  ✓ Creada StandardPage: {title}")
                else:
                    page = existing
                    self.stdout.write(f"  ✓ StandardPage existente: {title}")
            
            created_pages.add(page_key)
            
            # Procesar hijos recursivamente
            if node['children']:
                self._create_pages(node['children'], page, created_pages)
