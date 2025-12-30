"""
Management command para poblar páginas de Wagtail desde contenido HTML scrapeado
"""
import re
from pathlib import Path

from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

from cms.models import StandardPage, HomePage


def clean_html_for_wagtail(html_content):
    """
    Limpia y adapta HTML scrapeado para RichTextField de Wagtail

    Args:
        html_content: String con HTML crudo

    Returns:
        String con HTML limpio y adaptado
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Remover elementos no deseados
    for tag in soup.find_all(["script", "style", "nav", "header", "footer", "aside"]):
        tag.decompose()

    # Remover atributos de clases Bootstrap y otros atributos innecesarios
    # pero conservar estructura semántica
    for tag in soup.find_all(True):
        # Remover clases de Bootstrap pero conservar otras clases útiles
        if tag.get('class'):
            classes = tag.get('class', [])
            # Filtrar clases de Bootstrap pero conservar clases semánticas
            filtered_classes = [c for c in classes if not any(
                bootstrap_class in c.lower() for bootstrap_class in 
                ['container', 'row', 'col-md', 'col-sm', 'col-xs', 'col-lg', 'offset']
            )]
            if filtered_classes:
                tag['class'] = filtered_classes
            else:
                del tag['class']
        
        # Remover otros atributos innecesarios pero conservar id si es útil
        attrs_to_remove = ['style', 'data-', 'role']
        for attr in list(tag.attrs.keys()):
            if any(attr.startswith(prefix) for prefix in attrs_to_remove):
                del tag[attr]

    # Convertir URLs absolutas a relativas
    html_str = str(soup)

    # Imágenes: convertir URLs de WordPress a rutas estáticas
    html_str = re.sub(
        r'src="https://madmusic\.iccmu\.es/wp-content/uploads/([^"]+)"',
        r'src="/static/madmusic/images/\1"',
        html_str
    )

    # Links internos: convertir URLs absolutas a relativas
    html_str = re.sub(
        r'href="https://madmusic\.iccmu\.es/([^"]+)"',
        r'href="/madmusic/\1"',
        html_str
    )

    # Limpiar múltiples espacios y saltos de línea innecesarios
    html_str = re.sub(r'\n\s*\n\s*\n+', '\n\n', html_str)
    html_str = re.sub(r' +', ' ', html_str)

    # Asegurar que el HTML tenga estructura válida
    # Si no tiene etiquetas de párrafo, envolver texto en <p>
    if not re.search(r'<[ph]', html_str, re.IGNORECASE):
        # Es texto plano, convertir a párrafos
        paragraphs = [p.strip() for p in html_str.split('\n\n') if p.strip()]
        html_str = '\n'.join([f'<p>{p}</p>' for p in paragraphs])

    return html_str


def extract_content_from_html(html_path):
    """
    Extrae título y contenido principal de un archivo HTML scrapeado

    Args:
        html_path: Path al archivo HTML

    Returns:
        tuple: (titulo, contenido_html) o (None, None) si hay error
    """
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, "html.parser")

        # Extraer título
        titulo = None
        for selector in ["h1", "h2.title", ".entry-title", "title"]:
            elem = soup.select_one(selector)
            if elem:
                titulo = elem.get_text(strip=True)
                titulo = re.sub(r"\s+", " ", titulo)
                # Limpiar título si contiene "ICCMU" o "MadMusic"
                if "ICCMU" in titulo or "MadMusic" in titulo:
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
        main_section = soup.find("section", id="tools")
        if main_section:
            # Remover elementos no deseados
            for elem in main_section.find_all(["script", "style", "nav", "header", "footer", "aside"]):
                elem.decompose()
            # Remover contenedores innecesarios pero conservar el contenido interno
            # Buscar el contenido real dentro de section#tools
            content_container = main_section.find("article") or main_section.find("div", class_="pagina-detalle") or main_section.find("div", class_="content")
            if content_container:
                contenido = str(content_container)
            else:
                # Si no hay contenedor específico, buscar en divs con contenido
                # Buscar divs con clase col-md que contengan el contenido principal
                content_divs = main_section.find_all("div", class_=lambda x: x and any(c in ["col-md-9", "col-md-10", "col-md-12"] for c in x))
                if content_divs:
                    # Tomar el div más grande o el que tenga más contenido
                    contenido = str(max(content_divs, key=lambda d: len(str(d))))
                else:
                    # Usar todo el section
                    contenido = str(main_section)
        
        if not contenido:
            # Buscar en article o main
            article = soup.find("article") or soup.find("main")
            if article:
                for elem in article.find_all(["script", "style", "nav", "header", "footer", "aside"]):
                    elem.decompose()
                # Buscar contenido dentro de article
                content_div = article.find("div", class_="pagina-detalle") or article.find("div", class_="content")
                if content_div:
                    contenido = str(content_div)
                else:
                    contenido = str(article)
            else:
                contenido = "<p>Contenido de la página</p>"

        # Limpiar y adaptar para Wagtail
        contenido = clean_html_for_wagtail(contenido)

        # Limitar tamaño si es muy grande
        if len(contenido) > 100000:
            contenido = contenido[:100000] + "<p>...</p>"

        return titulo, contenido

    except Exception as e:
        return None, None


class Command(BaseCommand):
    help = "Pobla páginas de Wagtail desde contenido HTML scrapeado"

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
            help="Sobrescribir contenido existente",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simular sin hacer cambios",
        )

    def handle(self, *args, **options):
        scraped_dir = Path(options["scraped_dir"])
        overwrite = options["overwrite"]
        dry_run = options["dry_run"]

        if not scraped_dir.exists():
            self.stdout.write(
                self.style.ERROR(f"Directorio no encontrado: {scraped_dir}")
            )
            return

        # Obtener HomePage de madmusic
        home_page = HomePage.objects.filter(slug="madmusic-home").first()
        if not home_page:
            self.stdout.write(
                self.style.ERROR("No se encontró HomePage 'madmusic-home'")
            )
            return

        # Mapeo de slugs a archivos HTML (basado en poblar_madmusic_completo.py)
        slug_to_html = {
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

        pages_updated = 0
        pages_not_found = 0
        pages_skipped = 0

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("MIGRANDO CONTENIDO SCRAPEADO A WAGTAIL")
        self.stdout.write("=" * 80 + "\n")

        for slug, html_file in slug_to_html.items():
            html_path = scraped_dir / html_file

            # Buscar archivo con variaciones posibles
            if not html_path.exists():
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
                    if dry_run:
                        self.stdout.write(
                            self.style.WARNING(f"  [DRY-RUN] No encontrado: {html_file}")
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"  ⚠ No encontrado: {html_file}")
                        )
                    pages_not_found += 1
                    continue

            # Extraer contenido
            titulo, contenido = extract_content_from_html(html_path)
            if not titulo or not contenido:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠ Error extrayendo: {slug}")
                )
                pages_not_found += 1
                continue

            # Buscar página en Wagtail
            # Las páginas están bajo home_page con jerarquía de slugs
            slug_parts = slug.split("/")
            current_parent = home_page

            # Navegar por la jerarquía
            for i, slug_part in enumerate(slug_parts[:-1]):
                parent_page = StandardPage.objects.child_of(current_parent).filter(
                    slug=slug_part
                ).first()
                if parent_page:
                    current_parent = parent_page
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ⚠ Padre no encontrado: {'/'.join(slug_parts[:i+1])}"
                        )
                    )
                    pages_not_found += 1
                    break
            else:
                # Encontrar la página final
                final_slug = slug_parts[-1]
                wagtail_page = StandardPage.objects.child_of(current_parent).filter(
                    slug=final_slug
                ).first()

                if not wagtail_page:
                    self.stdout.write(
                        self.style.WARNING(f"  ⚠ Página no encontrada: {slug}")
                    )
                    pages_not_found += 1
                    continue

                # Verificar si ya tiene contenido
                if wagtail_page.body and len(str(wagtail_page.body).strip()) > 100 and not overwrite:
                    if dry_run:
                        self.stdout.write(
                            f"  [DRY-RUN] Omitiría (ya tiene contenido): {slug}"
                        )
                    else:
                        self.stdout.write(f"  - Ya tiene contenido: {slug}")
                    pages_skipped += 1
                    continue

                if dry_run:
                    self.stdout.write(
                        f"  [DRY-RUN] Actualizaría: {slug} - {titulo[:50]}"
                    )
                    self.stdout.write(
                        f"    Contenido length: {len(contenido)} caracteres"
                    )
                else:
                    # Actualizar página
                    wagtail_page.body = contenido
                    wagtail_page.save()
                    wagtail_page.save_revision().publish()
                    pages_updated += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✓ Actualizada: {slug} - {titulo[:50]}")
                    )

        # Resumen
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("RESUMEN:"))
        if dry_run:
            self.stdout.write("  [DRY-RUN] Simulación completada")
        self.stdout.write(f"  Actualizadas: {pages_updated}")
        self.stdout.write(f"  Omitidas: {pages_skipped}")
        self.stdout.write(f"  No encontradas: {pages_not_found}")
        self.stdout.write("=" * 80)

