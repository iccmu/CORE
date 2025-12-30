"""
Management command para poblar todas las páginas de Madmusic con contenido real desde HTML scrapeado
"""
import re
from pathlib import Path

from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

from core.models import Pagina, Proyecto


def extract_content_from_html(html_path):
    """Extraer título y contenido de un archivo HTML"""
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, "html.parser")

        # Extraer título - buscar en varios lugares
        titulo = None
        for selector in ["h1", "h2.title", ".entry-title", "title"]:
            elem = soup.select_one(selector)
            if elem:
                titulo = elem.get_text(strip=True)
                # Limpiar título
                titulo = re.sub(r"\s+", " ", titulo)
                if "ICCMU" in titulo or "MadMusic" in titulo:
                    # Intentar extraer solo la parte relevante
                    parts = titulo.split("|")
                    if len(parts) > 1:
                        titulo = parts[0].strip()
                if len(titulo) > 200:
                    titulo = titulo[:200]
                break

        if not titulo:
            titulo = "Página"

        # Extraer contenido principal
        contenido = None
        
        # Buscar en section#tools (contenido principal del sitio)
        main_section = soup.find("section", id="tools")
        if main_section:
            # Remover elementos no deseados
            for elem in main_section.find_all(["script", "style", "nav", "header", "footer"]):
                elem.decompose()
            contenido = str(main_section)
        
        # Si no hay section#tools, buscar en article o main
        if not contenido:
            article = soup.find("article") or soup.find("main")
            if article:
                for elem in article.find_all(["script", "style", "nav", "header", "footer"]):
                    elem.decompose()
                contenido = str(article)

        # Si aún no hay contenido, usar body sin header/footer
        if not contenido:
            body = soup.find("body")
            if body:
                # Remover header, footer, nav, scripts, styles
                for tag in body.find_all(["header", "footer", "nav", "script", "style"]):
                    tag.decompose()
                contenido = str(body)

        # Limpiar contenido HTML
        if contenido:
            # Convertir URLs absolutas a relativas para imágenes
            contenido = re.sub(
                r'src="https://madmusic\.iccmu\.es/wp-content/uploads/([^"]+)"',
                r'src="/static/madmusic/images/\1"',
                contenido
            )
            contenido = re.sub(
                r'href="https://madmusic\.iccmu\.es/([^"]+)"',
                r'href="/madmusic/\1"',
                contenido
            )
            # Limitar tamaño
            if len(contenido) > 100000:
                contenido = contenido[:100000] + "..."
        else:
            contenido = "<p>Contenido de la página</p>"

        return titulo, contenido

    except Exception as e:
        return None, None


class Command(BaseCommand):
    help = "Pobla todas las páginas de Madmusic con contenido real desde HTML scrapeado"

    def add_arguments(self, parser):
        parser.add_argument(
            "--scraped-dir",
            type=str,
            default="scraped_madmusic/html",
            help="Directorio con el HTML scrapeado",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Sobrescribir páginas existentes",
        )

    def handle(self, *args, **options):
        scraped_dir = Path(options["scraped_dir"])
        overwrite = options["overwrite"]

        if not scraped_dir.exists():
            self.stdout.write(
                self.style.ERROR(f"Directorio no encontrado: {scraped_dir}")
            )
            return

        # Obtener proyecto
        proyecto = Proyecto.objects.filter(slug="madmusic").first()
        if not proyecto:
            self.stdout.write(self.style.ERROR("Primero ejecuta: python manage.py poblar_madmusic_rapido"))
            return

        # Mapeo de slugs del menú a archivos HTML
        menu_pages = {
            "proyecto-madmusic": "proyecto-madmusic.html",
            "proyecto-madmusic/objetivos": "proyecto-madmusic/objetivos.html",
            "proyecto-madmusic/investigacion": "proyecto-madmusic/investigacion.html",
            "equipo": "equipo.html",
            "equipo/alvaro-torrente": "equipo/alvaro-torrente.html",
            "equipo/grupos-beneficiarios": "equipo/grupos-beneficiarios.html",
            "equipo/grupos-asociados": "equipo/grupos-asociados.html",
            "equipo/participantes": "equipo/participantes.html",
            "divulgacion-cientifica": "divulgacion-cientifica.html",
            "divulgacion-cientifica/archivos": "divulgacion-cientifica/archivos.html",
            "divulgacion-cientifica/cuadernos-de-musica-iberoamericana": "divulgacion-cientifica/cuadernos-de-musica-iberoamericana.html",
            "divulgacion-cientifica/articulos-en-revistas-cientificas": "divulgacion-cientifica/articulos-en-revistas-cientificas.html",
            "divulgacion-cientifica/publicaciones-en-abierto": "divulgacion-cientifica/publicaciones-en-abierto.html",
            "divulgacion-cientifica/congresos-madmusic": "divulgacion-cientifica/congresos-madmusic.html",
            "divulgacion-cientifica/publicaciones-madmusic-2": "divulgacion-cientifica/publicaciones-madmusic-2.html",
            "servicios-e-infraestructura": "servicios-e-infraestructura.html",
            "transferencia": "transferencia.html",
            "transferencia/empresas": "transferencia/empresas.html",
            "transferencia/conferencias": "transferencia/conferencias.html",
            "transferencia/conciertos": "transferencia/conciertos.html",
            "transferencia/exposiciones": "transferencia/exposiciones.html",
            "transferencia/divulgacion": "transferencia/divulgacion.html",
            "formacion-empleo": "formacion-empleo.html",
            "formacion-empleo/formacion": "formacion-empleo/formacion.html",
            "cursos-de-verano": "cursos-de-verano.html",
            "formacion-empleo/empleo": "formacion-empleo/empleo.html",
            "contacto": "contacto.html",
        }

        pages_created = 0
        pages_updated = 0
        pages_not_found = 0

        self.stdout.write("\nExtrayendo contenido real de las páginas...")

        for slug, html_file in menu_pages.items():
            html_path = scraped_dir / html_file

            # Buscar archivo con diferentes variaciones
            if not html_path.exists():
                # Intentar diferentes nombres
                possible_paths = [
                    scraped_dir / html_file,
                    scraped_dir / html_file.replace("/", "_"),
                    scraped_dir / html_file.replace("/", "-"),
                    scraped_dir / (slug + ".html"),
                    scraped_dir / (slug.replace("/", "_") + ".html"),
                ]

                found = False
                for test_path in possible_paths:
                    if test_path.exists():
                        html_path = test_path
                        found = True
                        break

                if not found:
                    self.stdout.write(
                        self.style.WARNING(f"  ⚠ No encontrado: {html_file}")
                    )
                    pages_not_found += 1
                    continue

            titulo, contenido = extract_content_from_html(html_path)

            if not titulo or not contenido:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠ Error extrayendo: {slug}")
                )
                pages_not_found += 1
                continue

            # Crear o actualizar página
            pagina, created = Pagina.objects.get_or_create(
                slug=slug,
                defaults={
                    "proyecto": proyecto,
                    "titulo": titulo,
                    "cuerpo": contenido,
                },
            )

            if created:
                pages_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ {slug[:50]}")
                )
            elif overwrite:
                pagina.titulo = titulo
                pagina.cuerpo = contenido
                pagina.proyecto = proyecto
                pagina.save()
                pages_updated += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  ↻ {slug[:50]}")
                )
            else:
                self.stdout.write(f"  - Ya existe: {slug}")

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("RESUMEN:"))
        self.stdout.write(f"  Creadas: {pages_created}")
        self.stdout.write(f"  Actualizadas: {pages_updated}")
        self.stdout.write(f"  No encontradas: {pages_not_found}")
        self.stdout.write("=" * 80)





