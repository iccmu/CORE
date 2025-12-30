"""
Comando para verificar que todas las páginas de Wagtail tienen contenido
"""
from django.core.management.base import BaseCommand
from django.test import Client
from django.conf import settings

from cms.models import StandardPage, HomePage


class Command(BaseCommand):
    help = "Verifica que todas las páginas de Wagtail tienen contenido"

    def handle(self, *args, **options):
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("VERIFICANDO PÁGINAS DE WAGTAIL")
        self.stdout.write("=" * 80 + "\n")

        # Obtener HomePage de madmusic
        home_page = HomePage.objects.filter(slug="madmusic-home").first()
        if not home_page:
            self.stdout.write(
                self.style.ERROR("No se encontró HomePage 'madmusic-home'")
            )
            return

        # Obtener todas las StandardPage
        all_pages = StandardPage.objects.live().descendant_of(home_page).order_by('url_path')
        
        pages_ok = 0
        pages_without_content = 0
        pages_with_errors = []

        for page in all_pages:
            try:
                # Verificar que tiene contenido
                body_content = str(page.body) if page.body else ""
                content_length = len(body_content.strip())
                
                if content_length < 50:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ⚠ Sin contenido: {page.url_path} ({content_length} chars)"
                        )
                    )
                    pages_without_content += 1
                else:
                    pages_ok += 1
                    # Mostrar información de la página
                    title_preview = page.title[:60] if len(page.title) > 60 else page.title
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✓ {page.url_path:<60} - {title_preview} ({content_length:,} chars)"
                        )
                    )
                    
            except Exception as e:
                pages_with_errors.append((page.url_path, str(e)))
                self.stdout.write(
                    self.style.ERROR(f"  ✗ {page.url_path} - Error: {str(e)[:50]}")
                )

        # Resumen
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("RESUMEN:"))
        self.stdout.write(f"  Páginas con contenido: {pages_ok}")
        self.stdout.write(f"  Páginas sin contenido: {pages_without_content}")
        self.stdout.write(f"  Páginas con errores: {len(pages_with_errors)}")
        self.stdout.write(f"  Total: {all_pages.count()}")
        
        if pages_without_content == 0 and len(pages_with_errors) == 0:
            self.stdout.write(self.style.SUCCESS("\n✓ Todas las páginas tienen contenido!"))
        
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("URLs de las páginas (accesibles en http://127.0.0.1:8000):")
        from wagtail.models import Site
        site = Site.objects.filter(hostname='127.0.0.1', port=8000).first()
        if site:
            for page in all_pages:
                # Usar url_path en lugar de url para evitar problemas con el Site
                url_path = page.url_path.replace('/madmusic-home', '/madmusic')
                self.stdout.write(f"  - http://127.0.0.1:8000{url_path}")
        else:
            for page in all_pages:
                url_path = page.url_path.replace('/madmusic-home', '/madmusic')
                self.stdout.write(f"  - http://127.0.0.1:8000{url_path}")
        self.stdout.write("=" * 80)

