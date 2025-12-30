"""
Comando para arreglar la configuración de Wagtail para desarrollo local
"""
from django.core.management.base import BaseCommand
from wagtail.models import Site, Page


class Command(BaseCommand):
    help = "Arregla la configuración de Wagtail para desarrollo local (127.0.0.1:8000)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--hostname",
            type=str,
            default="127.0.0.1",
            help="Hostname para desarrollo local",
        )
        parser.add_argument(
            "--port",
            type=int,
            default=8000,
            help="Puerto para desarrollo local",
        )

    def handle(self, *args, **options):
        hostname = options["hostname"]
        port = options["port"]

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("CONFIGURANDO WAGTAIL PARA DESARROLLO LOCAL")
        self.stdout.write("=" * 80 + "\n")

        # Obtener el root page de Wagtail
        wagtail_root = Page.objects.filter(depth=1).first()
        if not wagtail_root:
            self.stdout.write(
                self.style.ERROR("No se encontró el root page de Wagtail")
            )
            return

        # Buscar HomePage de madmusic
        home_page = None
        for page in Page.objects.filter(depth=2):
            if hasattr(page, 'slug') and page.slug == 'madmusic-home':
                home_page = page
                break

        if not home_page:
            self.stdout.write(
                self.style.ERROR("No se encontró HomePage 'madmusic-home'")
            )
            return

        # Buscar o crear Site para desarrollo local
        site, created = Site.objects.get_or_create(
            hostname=hostname,
            port=port,
            defaults={
                "site_name": "Madmusic (Local)",
                "root_page": home_page,
                "is_default_site": False,
            },
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Site creado: {hostname}:{port} -> {home_page.title}"
                )
            )
        else:
            # Actualizar si ya existe
            if site.root_page != home_page:
                site.root_page = home_page
                site.site_name = "Madmusic (Local)"
                site.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Site actualizado: {hostname}:{port} -> {home_page.title}"
                    )
                )
            else:
                self.stdout.write(
                    f"✓ Site ya existe: {hostname}:{port} -> {home_page.title}"
                )

        # Marcar como sitio por defecto si no hay otro
        default_site = Site.objects.filter(is_default_site=True).first()
        if not default_site:
            site.is_default_site = True
            site.save()
            self.stdout.write(
                self.style.SUCCESS(f"✓ Site marcado como predeterminado")
            )

        # Mostrar todos los sites
        self.stdout.write("\nSites configurados:")
        for s in Site.objects.all():
            default_marker = " (default)" if s.is_default_site else ""
            self.stdout.write(
                f"  - {s.hostname}:{s.port} -> {s.root_page}{default_marker}"
            )

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(
            self.style.SUCCESS(
                "Configuración completada. Ahora puedes acceder a las páginas en:\n"
                f"  http://{hostname}:{port}/"
            )
        )
        self.stdout.write("=" * 80)

