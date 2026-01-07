"""
Comando para configurar qué páginas aparecen en el menú de Wagtail
"""
from django.core.management.base import BaseCommand

from cms.models import StandardPage, HomePage, NewsIndexPage


class Command(BaseCommand):
    help = "Configura qué páginas aparecen en el menú principal de Wagtail"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simular sin hacer cambios",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("CONFIGURANDO MENÚ DE WAGTAIL")
        self.stdout.write("=" * 80 + "\n")

        # Obtener HomePage de madmusic
        home_page = HomePage.objects.filter(slug="madmusic-home").first()
        if not home_page:
            self.stdout.write(
                self.style.ERROR("No se encontró HomePage 'madmusic-home'")
            )
            return

        # Páginas principales que deben aparecer en el menú
        # Estas son las páginas de primer nivel
        main_menu_pages = [
            "proyecto-madmusic",
            "equipo",
            "divulgacion-cientifica",
            "servicios-e-infraestructura",
            "transferencia",
            "formacion-empleo",
        ]

        # Páginas especiales que también deben aparecer
        special_pages = [
            "noticias",  # NewsIndexPage
            "contacto",
        ]

        pages_updated = 0

        # Configurar páginas principales
        for slug in main_menu_pages:
            page = StandardPage.objects.child_of(home_page).filter(slug=slug).first()
            if page:
                if not page.show_in_menus:
                    if dry_run:
                        self.stdout.write(
                            f"  [DRY-RUN] Activaría menú: {slug}"
                        )
                    else:
                        page.show_in_menus = True
                        page.save()
                        pages_updated += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"  ✓ Menú activado: {slug}")
                        )
                else:
                    self.stdout.write(f"  - Ya en menú: {slug}")
            else:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠ No encontrada: {slug}")
                )

        # Configurar páginas especiales
        for slug in special_pages:
            if slug == "noticias":
                page = NewsIndexPage.objects.child_of(home_page).filter(slug=slug).first()
            else:
                page = StandardPage.objects.child_of(home_page).filter(slug=slug).first()

            if page:
                if not page.show_in_menus:
                    if dry_run:
                        self.stdout.write(
                            f"  [DRY-RUN] Activaría menú: {slug}"
                        )
                    else:
                        page.show_in_menus = True
                        page.save()
                        pages_updated += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"  ✓ Menú activado: {slug}")
                        )
                else:
                    self.stdout.write(f"  - Ya en menú: {slug}")
            else:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠ No encontrada: {slug}")
                )

        # Desactivar menú en páginas que NO deben aparecer en el menú principal
        # (solo aparecen como submenús)
        all_pages = StandardPage.objects.live().descendant_of(home_page)
        excluded_from_main_menu = [
            "proyecto-madmusic/objetivos",
            "proyecto-madmusic/investigacion",
            "equipo/alvaro-torrente",
            "equipo/grupos-beneficiarios",
            "equipo/grupos-asociados",
            "equipo/participantes",
            "divulgacion-cientifica/archivos",
            "divulgacion-cientifica/cuadernos-de-musica-iberoamericana",
            "divulgacion-cientifica/articulos-en-revistas-cientificas",
            "divulgacion-cientifica/publicaciones-en-abierto",
            "divulgacion-cientifica/congresos-madmusic",
            "divulgacion-cientifica/publicaciones-madmusic-2",
            "transferencia/empresas",
            "transferencia/conferencias",
            "transferencia/conciertos",
            "transferencia/exposiciones",
            "transferencia/divulgacion",
            "formacion-empleo/formacion",
            "formacion-empleo/empleo",
            "cursos-de-verano",  # Está en submenú de formacion-empleo
        ]

        for page in all_pages:
            # Construir el slug completo desde el path
            url_path = page.url_path.replace('/madmusic-home/', '')
            if url_path.endswith('/'):
                url_path = url_path[:-1]
            
            if url_path in excluded_from_main_menu:
                if page.show_in_menus:
                    if dry_run:
                        self.stdout.write(
                            f"  [DRY-RUN] Desactivaría menú: {url_path}"
                        )
                    else:
                        page.show_in_menus = False
                        page.save()
                        pages_updated += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"  ✓ Menú desactivado: {url_path}")
                        )

        # Resumen
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("RESUMEN:"))
        if dry_run:
            self.stdout.write("  [DRY-RUN] Simulación completada")
        self.stdout.write(f"  Páginas actualizadas: {pages_updated}")
        self.stdout.write("=" * 80)
        self.stdout.write("\nNota: Las páginas ahora aparecerán en el menú según su configuración.")
        self.stdout.write("Puedes editar 'show_in_menus' desde el admin de Wagtail en cada página.")
        self.stdout.write("=" * 80)



