"""
Management command para importar las noticias destacadas desde el HTML scrapeado
"""
import re
import shutil
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from core.models import Entrada, Proyecto


def parse_spanish_date(date_str):
    """Parsear fecha en formato español: '10 de noviembre de 2022'"""
    meses = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
        'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }
    
    # Buscar patrón: "10 de noviembre de 2022"
    match = re.search(r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})', date_str.lower())
    if match:
        dia = int(match.group(1))
        mes_nombre = match.group(2)
        año = int(match.group(3))
        
        mes = meses.get(mes_nombre)
        if mes:
            try:
                return datetime(año, mes, dia).date()
            except ValueError:
                pass
    
    return None


def extract_slug_from_url(url):
    """Extraer slug de una URL"""
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    # Remover trailing slash y extraer último segmento
    slug = path.split('/')[-1]
    return slug


class Command(BaseCommand):
    help = "Importa las noticias destacadas desde el archivo inicio.html scrapeado"

    def add_arguments(self, parser):
        parser.add_argument(
            "--scraped-dir",
            type=str,
            default="scraped_madmusic/html",
            help="Directorio con el HTML scrapeado",
        )
        parser.add_argument(
            "--images-dir",
            type=str,
            default="scraped_madmusic/images",
            help="Directorio con las imágenes scrapeadas",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Sobrescribir entradas existentes",
        )
        parser.add_argument(
            "--download-images",
            action="store_true",
            help="Descargar imágenes desde URLs si no están en el directorio local",
        )

    def find_image_file(self, image_url, images_dir):
        """Buscar archivo de imagen en el directorio scrapeado"""
        if not image_url:
            return None
        
        # Extraer nombre del archivo de la URL
        parsed_url = urlparse(image_url)
        filename = Path(parsed_url.path).name
        
        if not filename:
            return None
        
        # Buscar en el directorio de imágenes
        images_path = Path(images_dir)
        if not images_path.exists():
            return None
        
        # Buscar archivo exacto
        image_file = images_path / filename
        if image_file.exists():
            return image_file
        
        # Extraer nombre base (sin dimensiones como -350x350)
        # Ejemplo: "Elena-y-Malvina-350x350.jpg" -> "Elena-y-Malvina"
        base_name = filename
        # Remover dimensiones comunes: -350x350, -300x300, etc.
        base_name = re.sub(r'-\d+x\d+', '', base_name)
        # Remover extensión
        base_name_without_ext = Path(base_name).stem
        
        # Buscar archivos que contengan el nombre base
        for ext in ['.jpg', '.jpeg', '.png', '.gif']:
            # Buscar archivos que empiecen con el nombre base
            pattern = f"{base_name_without_ext}*{ext}"
            matches = list(images_path.glob(pattern))
            if matches:
                # Preferir el que tenga dimensiones similares o el más pequeño
                # Ordenar por nombre (los sin sufijos numéricos primero)
                matches.sort(key=lambda x: (len(x.name.split('_')), x.name))
                return matches[0]
        
        # Si no se encuentra, buscar por partes del nombre
        name_parts = base_name_without_ext.split('-')
        if len(name_parts) > 1:
            # Buscar con las primeras partes del nombre
            search_pattern = '-'.join(name_parts[:3])  # Primeras 3 partes
            for ext in ['.jpg', '.jpeg', '.png', '.gif']:
                matches = list(images_path.glob(f"{search_pattern}*{ext}"))
                if matches:
                    matches.sort(key=lambda x: (len(x.name.split('_')), x.name))
                    return matches[0]
        
        return None

    def download_image(self, image_url):
        """Descargar imagen desde URL"""
        try:
            response = requests.get(image_url, timeout=10, stream=True)
            response.raise_for_status()
            return ContentFile(response.content)
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"  ⚠ Error descargando imagen {image_url}: {e}")
            )
            return None

    def handle(self, *args, **options):
        scraped_dir = Path(options["scraped_dir"])
        images_dir = Path(options["images_dir"])
        overwrite = options["overwrite"]
        download_images = options["download_images"]

        if not scraped_dir.exists():
            self.stdout.write(
                self.style.ERROR(f"Directorio no encontrado: {scraped_dir}")
            )
            return

        # Obtener o crear proyecto Madmusic
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

        # Leer archivo inicio.html
        inicio_html = scraped_dir / "inicio.html"
        if not inicio_html.exists():
            self.stdout.write(
                self.style.ERROR(f"Archivo no encontrado: {inicio_html}")
            )
            return

        self.stdout.write(f"Leyendo {inicio_html}...")
        with open(inicio_html, "r", encoding="utf-8") as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, "html.parser")

        # Buscar sección de teasers
        teasers_section = soup.find("section", id="teasers")
        if not teasers_section:
            self.stdout.write(
                self.style.WARNING("No se encontró la sección #teasers")
            )
            return

        # Buscar todos los elementos iccmuteaser
        teasers = teasers_section.find_all("div", class_="iccmuteaser")
        self.stdout.write(f"Encontradas {len(teasers)} noticias destacadas")

        entradas_created = 0
        entradas_updated = 0
        entradas_skipped = 0

        for teaser in teasers:
            try:
                # Buscar el enlace padre
                link = teaser.find_parent("a")
                if not link:
                    continue

                url = link.get("href", "")
                if not url:
                    continue

                # Normalizar URL (convertir a absoluta si es relativa)
                if url.startswith('/'):
                    url = urljoin('https://madmusic.iccmu.es', url)
                elif not url.startswith('http'):
                    url = urljoin('https://madmusic.iccmu.es/', url)

                # Extraer slug de la URL
                slug = extract_slug_from_url(url)
                if not slug:
                    continue

                # Extraer título
                title_elem = teaser.find("h1", class_="title")
                titulo = title_elem.get_text(strip=True) if title_elem else ""

                if not titulo:
                    continue

                # Extraer fecha
                date_elem = teaser.find("p", class_="date")
                fecha_publicacion = None
                if date_elem:
                    date_text = date_elem.get_text()
                    fecha_publicacion = parse_spanish_date(date_text)

                # Extraer resumen
                desc_elem = teaser.find("p", class_="description")
                resumen = desc_elem.get_text(strip=True) if desc_elem else ""

                # Extraer imagen
                img_elem = teaser.find("img")
                imagen_url = None
                imagen_file = None
                if img_elem:
                    imagen_url = img_elem.get("src", "")
                    
                    # Buscar imagen en directorio local
                    if imagen_url:
                        imagen_file = self.find_image_file(imagen_url, images_dir)
                        if imagen_file:
                            self.stdout.write(
                                f"  [✓] Imagen encontrada: {imagen_file.name}"
                            )
                        else:
                            self.stdout.write(
                                f"  [⚠] Imagen no encontrada: {Path(urlparse(imagen_url).path).name}"
                            )
                            # Si no se encuentra y se permite descargar, intentar descargar
                            if download_images:
                                self.stdout.write(
                                    f"  [→] Descargando imagen: {imagen_url}"
                                )
                                image_content = self.download_image(imagen_url)
                                if image_content:
                                    # Guardar temporalmente para procesar después
                                    imagen_file = image_content

                # Buscar el archivo HTML completo de la entrada
                entrada_html = scraped_dir / f"{slug}.html"
                cuerpo = resumen  # Por defecto usar el resumen

                if entrada_html.exists():
                    try:
                        with open(entrada_html, "r", encoding="utf-8") as ef:
                            entrada_content = ef.read()
                        entrada_soup = BeautifulSoup(entrada_content, "html.parser")

                        # Extraer contenido completo - buscar específicamente el div.description
                        description_div = entrada_soup.find("div", class_="description")
                        if description_div:
                            # Remover scripts y estilos
                            for script in description_div(["script", "style"]):
                                script.decompose()
                            # Limpiar atributos innecesarios pero mantener estructura HTML básica
                            for tag in description_div.find_all():
                                # Mantener solo atributos esenciales (href para enlaces, src para imágenes)
                                if tag.name == 'a' and 'href' in tag.attrs:
                                    tag.attrs = {'href': tag.attrs['href']}
                                elif tag.name == 'img' and 'src' in tag.attrs:
                                    tag.attrs = {'src': tag.attrs['src'], 'alt': tag.attrs.get('alt', '')}
                                else:
                                    # Para otros tags, limpiar todos los atributos excepto los esenciales
                                    clean_attrs = {}
                                    if 'href' in tag.attrs:
                                        clean_attrs['href'] = tag.attrs['href']
                                    if 'src' in tag.attrs:
                                        clean_attrs['src'] = tag.attrs['src']
                                    if 'alt' in tag.attrs:
                                        clean_attrs['alt'] = tag.attrs['alt']
                                    tag.attrs = clean_attrs
                            
                            # Obtener solo el contenido interno del div.description
                            cuerpo = ''.join(str(child) for child in description_div.children)
                            # Limpiar espacios múltiples en HTML
                            cuerpo = re.sub(r'\s+', ' ', cuerpo)
                            cuerpo = re.sub(r'>\s+<', '><', cuerpo)
                        else:
                            # Fallback: buscar en main_content
                            main_content = (
                                entrada_soup.find("main")
                                or entrada_soup.find("section", id="tools")
                                or entrada_soup.find("article")
                            )
                            if main_content:
                                # Remover scripts y estilos
                                for script in main_content(["script", "style"]):
                                    script.decompose()
                                cuerpo = main_content.get_text(separator="\n", strip=True)
                                # Limpiar espacios múltiples
                                cuerpo = re.sub(r"\n{3,}", "\n\n", cuerpo)
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(
                                f"  ⚠ Error leyendo {entrada_html}: {e}"
                            )
                        )

                # Crear o actualizar entrada
                entrada, created = Entrada.objects.get_or_create(
                    slug=slug,
                    defaults={
                        "proyecto": proyecto,
                        "titulo": titulo[:200],
                        "resumen": resumen[:500] if resumen else "",
                        "cuerpo": cuerpo[:10000] if len(cuerpo) > 10000 else cuerpo,
                        "fecha_publicacion": fecha_publicacion or datetime.now().date(),
                        "url_original": url,
                    },
                )

                # Asociar imagen si existe
                if imagen_file and (created or overwrite or not entrada.imagen_destacada):
                    try:
                        if isinstance(imagen_file, Path):
                            # Es un archivo local, copiarlo
                            with open(imagen_file, 'rb') as f:
                                file_name = imagen_file.name
                                entrada.imagen_destacada.save(
                                    file_name,
                                    ContentFile(f.read()),
                                    save=False
                                )
                        elif isinstance(imagen_file, ContentFile):
                            # Es contenido descargado
                            file_name = Path(urlparse(imagen_url).path).name if imagen_url else "imagen.jpg"
                            entrada.imagen_destacada.save(
                                file_name,
                                imagen_file,
                                save=False
                            )
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(
                                f"  ⚠ Error guardando imagen para {slug}: {e}"
                            )
                        )

                if created:
                    entrada.save()  # Guardar con la imagen si se asoció
                    entradas_created += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✓ Creada: {slug} - {titulo[:50]}"
                        )
                    )
                elif overwrite:
                    entrada.titulo = titulo[:200]
                    entrada.resumen = resumen[:500] if resumen else ""
                    entrada.cuerpo = cuerpo[:10000] if len(cuerpo) > 10000 else cuerpo
                    if fecha_publicacion:
                        entrada.fecha_publicacion = fecha_publicacion
                    entrada.url_original = url
                    entrada.save()
                    entradas_updated += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"  ↻ Actualizada: {slug}")
                    )
                else:
                    # Actualizar URL original si no existe
                    if not entrada.url_original:
                        entrada.url_original = url
                        entrada.save()
                    
                    if imagen_file and not entrada.imagen_destacada:
                        # Actualizar solo la imagen si no existe
                        try:
                            if isinstance(imagen_file, Path):
                                with open(imagen_file, 'rb') as f:
                                    file_name = imagen_file.name
                                    entrada.imagen_destacada.save(
                                        file_name,
                                        ContentFile(f.read()),
                                        save=True
                                    )
                            elif isinstance(imagen_file, ContentFile):
                                file_name = Path(urlparse(imagen_url).path).name if imagen_url else "imagen.jpg"
                                entrada.imagen_destacada.save(
                                    file_name,
                                    imagen_file,
                                    save=True
                                )
                            self.stdout.write(f"  ↻ Imagen agregada: {slug}")
                        except Exception as e:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"  ⚠ Error agregando imagen a {slug}: {e}"
                                )
                            )
                    entradas_skipped += 1
                    self.stdout.write(f"  - Ya existe: {slug}")

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ✗ Error procesando teaser: {e}")
                )
                entradas_skipped += 1

        # Resumen
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("RESUMEN:"))
        self.stdout.write(f"  Entradas creadas: {entradas_created}")
        self.stdout.write(f"  Entradas actualizadas: {entradas_updated}")
        self.stdout.write(f"  Entradas omitidas: {entradas_skipped}")
        self.stdout.write("=" * 80)

