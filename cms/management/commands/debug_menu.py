"""
Comando para debuggear el estado del menú de Wagtail
"""
from django.core.management.base import BaseCommand
from cms.models import StandardPage, HomePage, NewsIndexPage
from wagtail.models import Page


class Command(BaseCommand):
    help = "Muestra el estado actual del menú de Wagtail"

    def handle(self, *args, **options):
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("ESTADO DEL MENÚ DE WAGTAIL")
        self.stdout.write("=" * 80 + "\n")

        # Obtener HomePage de madmusic
        home_page = HomePage.objects.filter(slug="madmusic-home").first()
        if not home_page:
            self.stdout.write(
                self.style.ERROR("❌ No se encontró HomePage 'madmusic-home'")
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f"✓ HomePage encontrada: {home_page.title}")
        )
        self.stdout.write(f"  URL: {home_page.url}")
        self.stdout.write(f"  Live: {home_page.live}")
        self.stdout.write()

        # Obtener páginas de nivel 1 (hijos directos de home)
        level1_pages = (
            Page.objects.child_of(home_page).live().filter(show_in_menus=True).specific()
        )

        self.stdout.write("NIVEL 1 (Páginas principales):")
        self.stdout.write("-" * 80)

        if not level1_pages:
            self.stdout.write(
                self.style.WARNING("  ⚠ No hay páginas de nivel 1 con show_in_menus=True")
            )
        else:
            for page in level1_pages:
                status = "✓" if page.show_in_menus else "✗"
                self.stdout.write(
                    f"\n  {status} {page.title}"
                )
                self.stdout.write(f"     Slug: {page.slug}")
                self.stdout.write(f"     URL: {page.url}")
                self.stdout.write(f"     Type: {page.__class__.__name__}")

                # Obtener hijos (nivel 2)
                children = Page.objects.child_of(page).live().specific()
                if children:
                    self.stdout.write(f"     Subpáginas ({children.count()}):")
                    for child in children:
                        child_status = "✓" if child.show_in_menus else "✗"
                        self.stdout.write(
                            f"       {child_status} {child.title} ({child.slug})"
                        )

        # Resumen
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("RESUMEN:")
        self.stdout.write(f"  Total páginas nivel 1: {level1_pages.count()}")
        
        total_children = 0
        for page in level1_pages:
            children_count = Page.objects.child_of(page).live().count()
            total_children += children_count
        
        self.stdout.write(f"  Total páginas nivel 2: {total_children}")
        self.stdout.write("=" * 80)
        self.stdout.write()
