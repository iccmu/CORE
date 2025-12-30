"""
Comando para debuggear el menú de Wagtail
"""
from django.core.management.base import BaseCommand
from django.template import Context, Template
from django.test import RequestFactory

from cms.models import HomePage
from cms.templatetags.cms_tags import get_menu_items


class Command(BaseCommand):
    help = "Debug del menú de Wagtail"

    def handle(self, *args, **options):
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("DEBUG DEL MENÚ DE WAGTAIL")
        self.stdout.write("=" * 80 + "\n")

        # Obtener HomePage
        home_page = HomePage.objects.filter(slug='madmusic-home').first()
        if not home_page:
            self.stdout.write(self.style.ERROR("No se encontró HomePage 'madmusic-home'"))
            return

        # Obtener items del menú
        menu_items = get_menu_items(home_page, None, 2)
        
        self.stdout.write(f"Total de items en menú: {len(menu_items)}\n")
        
        for item in menu_items:
            self.stdout.write(f"  - {item['title']}")
            self.stdout.write(f"    URL: {item['url']}")
            self.stdout.write(f"    Hijos: {len(item['children'])}")
            if item['children']:
                for child in item['children']:
                    self.stdout.write(f"      • {child['title']} - {child['url']}")
            self.stdout.write("")

        # Probar renderizado del template
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("PROBANDO RENDERIZADO DEL TEMPLATE")
        self.stdout.write("=" * 80 + "\n")

        try:
            from django.template.loader import get_template
            template = get_template('cms/menu.html')
            context = Context({
                'menu_items': menu_items,
                'current_page': None,
            })
            rendered = template.render(context)
            self.stdout.write(self.style.SUCCESS("✓ Template renderizado correctamente"))
            self.stdout.write(f"Longitud del HTML: {len(rendered)} caracteres")
            self.stdout.write(f"\nPrimeras 500 caracteres:\n{rendered[:500]}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error renderizando template: {e}"))

        self.stdout.write("\n" + "=" * 80)

