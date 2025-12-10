"""
Management command para poblar todas las páginas de Madmusic desde el contenido scrapeado
"""
import os
import re
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from core.models import Entrada, Pagina, Proyecto


class Command(BaseCommand):
    help = "Pobla todas las páginas de Madmusic desde el contenido scrapeado"

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

        # Crear o obtener proyecto Madmusic
        proyecto, created = Proyecto.objects.get_or_create(
            slug="madmusic",
            defaults={
                "titulo": "MadMusic-CM",
                "acronimo": "MADMUSIC",
                "resumen": "Espacios, géneros y públicos de la música en Madrid (ss. XVII-XX)",
                "cuerpo": "El proyecto MadMusic propone investigar, publicar e interpretar obras del patrimonio musical madrileño de los siglos XVII-XX olvidadas por estudiosos y gestores, proporcionando obras de calidad a programadores culturales para conocimiento del público.",
                "fecha_inicio": "2020-01-01",
                "url_oficial": "https://madmusic.iccmu.es/",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"✓ Proyecto creado: {proyecto.titulo}"))
        else:
            self.stdout.write(f"  Proyecto existente: {proyecto.titulo}")

        # Mapeo de slugs del menú a slugs de archivos scrapeados
        menu_pages = {
            # Acerca de MadMusic
            "proyecto-madmusic": "proyecto-madmusic.html",
            "proyecto-madmusic/objetivos": "proyecto-madmusic/objetivos.html",
            "proyecto-madmusic/investigacion": "proyecto-madmusic/investigacion.html",
            # Equipo
            "equipo": "equipo.html",
            "equipo/alvaro-torrente": "equipo/alvaro-torrente.html",
            "equipo/grupos-beneficiarios": "equipo/grupos-beneficiarios.html",
            "equipo/grupos-asociados": "equipo/grupos-asociados.html",
            "equipo/participantes": "equipo/participantes.html",
            # Resultados científicos
            "divulgacion-cientifica": "divulgacion-cientifica.html",
            "divulgacion-cientifica/archivos": "divulgacion-cientifica/archivos.html",
            "divulgacion-cientifica/cuadernos-de-musica-iberoamericana": "divulgacion-cientifica/cuadernos-de-musica-iberoamericana.html",
            "divulgacion-cientifica/articulos-en-revistas-cientificas": "divulgacion-cientifica/articulos-en-revistas-cientificas.html",
            "divulgacion-cientifica/publicaciones-en-abierto": "divulgacion-cientifica/publicaciones-en-abierto.html",
            "divulgacion-cientifica/congresos-madmusic": "divulgacion-cientifica/congresos-madmusic.html",
            "divulgacion-cientifica/publicaciones-madmusic-2": "divulgacion-cientifica/publicaciones-madmusic-2.html",
            # Servicios
            "servicios-e-infraestructura": "servicios-e-infraestructura.html",
            # Transferencia
            "transferencia": "transferencia.html",
            "transferencia/empresas": "transferencia/empresas.html",
            "transferencia/conferencias": "transferencia/conferencias.html",
            "transferencia/conciertos": "transferencia/conciertos.html",
            "transferencia/exposiciones": "transferencia/exposiciones.html",
            "transferencia/divulgacion": "transferencia/divulgacion.html",
            # Formación
            "formacion-empleo": "formacion-empleo.html",
            "formacion-empleo/formacion": "formacion-empleo/formacion.html",
            "cursos-de-verano": "cursos-de-verano.html",
            "formacion-empleo/empleo": "formacion-empleo/empleo.html",
            # Otros
            "contacto": "contacto.html",
            "actualidad-2": "actualidad-2.html",  # Noticias
        }

        # Procesar todas las páginas del menú
        pages_created = 0
        pages_updated = 0
        pages_skipped = 0

        for slug_menu, html_file in menu_pages.items():
            html_path = scraped_dir / html_file

            if not html_path.exists():
                # Intentar buscar el archivo con diferentes variaciones
                possible_names = [
                    html_file,
                    html_file.replace("/", "_"),
                    html_file.replace("/", "-"),
                    slug_menu + ".html",
                    slug_menu.replace("/", "_") + ".html",
                ]

                found = False
                for name in possible_names:
                    test_path = scraped_dir / name
                    if test_path.exists():
                        html_path = test_path
                        found = True
                        break

                if not found:
                    self.stdout.write(
                        self.style.WARNING(f"  ⚠ Archivo no encontrado: {html_file}")
                    )
                    pages_skipped += 1
                    continue

            try:
                with open(html_path, "r", encoding="utf-8") as f:
                    html_content = f.read()

                soup = BeautifulSoup(html_content, "html.parser")

                # Extraer título
                title_tag = soup.find("h1") or soup.find("h2") or soup.find("title")
                if title_tag:
                    titulo = title_tag.get_text(strip=True)
                    # Limpiar título
                    titulo = re.sub(r"\s+", " ", titulo)
                    if len(titulo) > 200:
                        titulo = titulo[:200]
                else:
                    titulo = slug_menu.replace("-", " ").replace("/", " - ").title()

                # Extraer contenido principal
                main_content = soup.find("main") or soup.find("section", id="tools") or soup.find("article")
                if main_content:
                    # Remover scripts y estilos
                    for script in main_content(["script", "style"]):
                        script.decompose()
                    cuerpo = main_content.get_text(separator="\n", strip=True)
                    # También intentar obtener HTML limpio
                    cuerpo_html = str(main_content)
                else:
                    # Si no hay main, buscar en body
                    body = soup.find("body")
                    if body:
                        for script in body(["script", "style", "header", "footer", "nav"]):
                            script.decompose()
                        cuerpo = body.get_text(separator="\n", strip=True)
                        cuerpo_html = str(body)
                    else:
                        cuerpo = "Contenido de la página"
                        cuerpo_html = "<p>Contenido de la página</p>"

                # Limpiar y limitar cuerpo
                cuerpo = re.sub(r"\n{3,}", "\n\n", cuerpo)
                if len(cuerpo) > 10000:
                    cuerpo = cuerpo[:10000] + "..."
                if len(cuerpo_html) > 50000:
                    cuerpo_html = cuerpo_html[:50000]

                # Usar HTML si está disponible, sino texto plano
                cuerpo_final = cuerpo_html if len(cuerpo_html) > len(cuerpo) else cuerpo

                # Crear o actualizar página
                pagina, created = Pagina.objects.get_or_create(
                    slug=slug_menu,
                    defaults={
                        "proyecto": proyecto,
                        "titulo": titulo,
                        "cuerpo": cuerpo_final,
                    },
                )

                if created:
                    pages_created += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✓ Creada: {slug_menu} - {titulo[:50]}")
                    )
                elif overwrite:
                    pagina.titulo = titulo
                    pagina.cuerpo = cuerpo_final
                    pagina.proyecto = proyecto
                    pagina.save()
                    pages_updated += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"  ↻ Actualizada: {slug_menu}")
                    )
                else:
                    pages_skipped += 1
                    self.stdout.write(f"  - Ya existe: {slug_menu}")

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ✗ Error procesando {slug_menu}: {e}")
                )
                pages_skipped += 1

        # Procesar entradas/noticias desde las categorías scrapeadas
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("Procesando entradas/noticias...")

        # Buscar páginas de categorías que contengan entradas
        category_files = [
            "category/noticias-actualidad.html",
            "category/investigacion/proyecto-madmusic.html",
            "category/estrenos.html",
            "category/transferencia.html",
            "category/difusion.html",
        ]

        entradas_created = 0
        for cat_file in category_files:
            cat_path = scraped_dir / cat_file
            if cat_path.exists():
                try:
                    with open(cat_path, "r", encoding="utf-8") as f:
                        html_content = f.read()

                    soup = BeautifulSoup(html_content, "html.parser")
                    # Buscar enlaces a entradas individuales
                    entrada_links = soup.find_all("a", href=re.compile(r"/\d{4}/|/[a-z-]+/$"))

                    for link in entrada_links[:10]:  # Limitar a 10 por categoría
                        href = link.get("href", "")
                        if not href or "category" in href or "tag" in href:
                            continue

                        # Extraer slug de la URL
                        slug_match = re.search(r"/([^/]+)/?$", href)
                        if slug_match:
                            entrada_slug = slug_match.group(1)
                            if entrada_slug and len(entrada_slug) > 5:
                                # Buscar si existe el HTML de esta entrada
                                entrada_html = scraped_dir / f"{entrada_slug}.html"
                                if entrada_html.exists():
                                    try:
                                        with open(entrada_html, "r", encoding="utf-8") as ef:
                                            entrada_content = ef.read()
                                        entrada_soup = BeautifulSoup(entrada_content, "html.parser")

                                        titulo_elem = entrada_soup.find("h1") or entrada_soup.find("title")
                                        titulo_entrada = titulo_elem.get_text(strip=True) if titulo_elem else entrada_slug.replace("-", " ").title()

                                        cuerpo_elem = entrada_soup.find("main") or entrada_soup.find("article") or entrada_soup.find("section", id="tools")
                                        if cuerpo_elem:
                                            for script in cuerpo_elem(["script", "style"]):
                                                script.decompose()
                                            cuerpo_entrada = cuerpo_elem.get_text(separator="\n", strip=True)
                                        else:
                                            cuerpo_entrada = f"Contenido de {titulo_entrada}"

                                        # Buscar fecha
                                        fecha_elem = entrada_soup.find(class_=re.compile("date|fecha"))
                                        fecha = None
                                        if fecha_elem:
                                            fecha_text = fecha_elem.get_text()
                                            fecha_match = re.search(r"(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})", fecha_text)
                                            if fecha_match:
                                                # Intentar parsear fecha (simplificado)
                                                pass

                                        Entrada.objects.get_or_create(
                                            slug=entrada_slug,
                                            defaults={
                                                "proyecto": proyecto,
                                                "titulo": titulo_entrada[:200],
                                                "resumen": cuerpo_entrada[:500] if len(cuerpo_entrada) > 100 else "",
                                                "cuerpo": cuerpo_entrada,
                                            },
                                        )
                                        entradas_created += 1
                                    except Exception as e:
                                        pass

                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"  ⚠ Error procesando categoría {cat_file}: {e}")
                    )

        # Resumen
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("RESUMEN:"))
        self.stdout.write(f"  Páginas creadas: {pages_created}")
        self.stdout.write(f"  Páginas actualizadas: {pages_updated}")
        self.stdout.write(f"  Páginas omitidas: {pages_skipped}")
        self.stdout.write(f"  Entradas creadas: {entradas_created}")
        self.stdout.write("=" * 80)
