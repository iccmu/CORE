"""
Management command para importar imágenes scrapeadas a Wagtail Images
"""
import os
import re
from pathlib import Path
from urllib.parse import urlparse

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from wagtail.images.models import Image

from cms.models import NewsPage
from core.models import Entrada


class Command(BaseCommand):
    help = "Importa imágenes desde scraped_madmusic/images a Wagtail Images"

    def add_arguments(self, parser):
        parser.add_argument(
            "--images-dir",
            type=str,
            default="scraped_madmusic/images",
            help="Directorio con las imágenes scrapeadas",
        )
        parser.add_argument(
            "--static-images-dir",
            type=str,
            default="madmusic_app/static/madmusic/images",
            help="Directorio con imágenes estáticas (fallback)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simular sin hacer cambios",
        )
        parser.add_argument(
            "--associate-news",
            action="store_true",
            help="Asociar imágenes a NewsPage por nombre de archivo",
        )
        parser.add_argument(
            "--import-all",
            action="store_true",
            help="Importar todas las imágenes del directorio scrapeado a Wagtail",
        )

    def find_image_file(self, image_name, images_dir, static_dir):
        """
        Buscar archivo de imagen en los directorios disponibles

        Args:
            image_name: Nombre del archivo de imagen
            images_dir: Directorio de imágenes scrapeadas
            static_dir: Directorio de imágenes estáticas

        Returns:
            Path al archivo o None si no se encuentra
        """
        # Normalizar nombre (remover dimensiones como -350x350)
        base_name = image_name
        base_name = re.sub(r'-\d+x\d+', '', base_name)
        base_name_without_ext = Path(base_name).stem

        # Buscar en directorio scrapeado primero
        images_path = Path(images_dir)
        if images_path.exists():
            # Buscar archivo exacto
            exact_match = images_path / image_name
            if exact_match.exists():
                return exact_match

            # Buscar por nombre base
            for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                pattern = f"{base_name_without_ext}*{ext}"
                matches = list(images_path.glob(pattern))
                if matches:
                    # Preferir el más pequeño (sin sufijos numéricos)
                    matches.sort(key=lambda x: (len(x.name.split('_')), x.name))
                    return matches[0]

        # Buscar en directorio estático como fallback
        static_path = Path(static_dir)
        if static_path.exists():
            exact_match = static_path / image_name
            if exact_match.exists():
                return exact_match

            for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                pattern = f"{base_name_without_ext}*{ext}"
                matches = list(static_path.glob(pattern))
                if matches:
                    matches.sort(key=lambda x: (len(x.name.split('_')), x.name))
                    return matches[0]

        return None

    def import_image_to_wagtail(self, image_path, title=None, dry_run=False):
        """
        Importar una imagen a Wagtail Images

        Args:
            image_path: Path al archivo de imagen
            title: Título para la imagen en Wagtail
            dry_run: Si es True, solo simula

        Returns:
            Image object o None
        """
        if not image_path or not image_path.exists():
            return None

        # Generar título si no se proporciona
        if not title:
            title = image_path.stem.replace('-', ' ').replace('_', ' ').title()

        # Verificar si ya existe por título
        existing = Image.objects.filter(title=title).first()
        if existing:
            return existing

        if dry_run:
            self.stdout.write(f"  [DRY-RUN] Importaría: {image_path.name} -> {title}")
            return None

        try:
            with open(image_path, 'rb') as f:
                wagtail_image = Image(title=title, file=File(f, name=image_path.name))
                wagtail_image.save()
                return wagtail_image
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  ✗ Error importando {image_path.name}: {e}")
            )
            return None

    def associate_image_to_news(self, news_page, image_name, images_dir, static_dir, dry_run=False):
        """
        Asociar imagen a NewsPage por nombre de archivo

        Args:
            news_page: NewsPage object
            image_name: Nombre del archivo de imagen
            images_dir: Directorio de imágenes scrapeadas
            static_dir: Directorio de imágenes estáticas
            dry_run: Si es True, solo simula
        """
        # Buscar archivo de imagen
        image_path = self.find_image_file(image_name, images_dir, static_dir)
        if not image_path:
            return False

        # Importar a Wagtail
        wagtail_image = self.import_image_to_wagtail(
            image_path,
            title=f"{news_page.title} - Imagen destacada",
            dry_run=dry_run
        )

        if not wagtail_image:
            return False

        # Asociar a NewsPage
        if not dry_run:
            news_page.featured_image = wagtail_image
            news_page.save()

        return True

    def handle(self, *args, **options):
        # Convertir rutas relativas a absolutas usando BASE_DIR
        images_dir_str = options["images_dir"]
        static_dir_str = options["static_images_dir"]
        
        # Si son rutas relativas, convertir a absolutas
        if not os.path.isabs(images_dir_str):
            images_dir = Path(settings.BASE_DIR) / images_dir_str
        else:
            images_dir = Path(images_dir_str)
            
        if not os.path.isabs(static_dir_str):
            static_dir = Path(settings.BASE_DIR) / static_dir_str
        else:
            static_dir = Path(static_dir_str)
        
        dry_run = options["dry_run"]
        associate_news = options["associate_news"]

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("IMPORTANDO IMÁGENES A WAGTAIL")
        self.stdout.write("=" * 80 + "\n")
        self.stdout.write(f"Directorio de imágenes scrapeadas: {images_dir}")
        self.stdout.write(f"Directorio de imágenes estáticas: {static_dir}\n")

        if not images_dir.exists() and not static_dir.exists():
            self.stdout.write(
                self.style.ERROR("No se encontraron directorios de imágenes")
            )
            return

        images_imported = 0
        images_skipped = 0
        news_associated = 0
        import_all = options.get("import_all", False)

        # Importar todas las imágenes del directorio scrapeado si se solicita
        if import_all:
            self.stdout.write("Importando todas las imágenes del directorio scrapeado...\n")
            if images_dir.exists():
                # Obtener todas las imágenes del directorio
                image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
                all_images = []
                for ext in image_extensions:
                    all_images.extend(images_dir.glob(f"*{ext}"))
                    all_images.extend(images_dir.glob(f"*{ext.upper()}"))
                
                self.stdout.write(f"  Encontradas {len(all_images)} imágenes en el directorio\n")
                
                for image_path in all_images:
                    # Generar título desde el nombre del archivo
                    title = image_path.stem.replace('-', ' ').replace('_', ' ').title()
                    # Limpiar sufijos comunes como dimensiones
                    title = re.sub(r'\s+\d+x\d+.*$', '', title)
                    title = re.sub(r'\s+\d+$', '', title)
                    
                    wagtail_image = self.import_image_to_wagtail(
                        image_path,
                        title=title,
                        dry_run=dry_run
                    )
                    if wagtail_image:
                        images_imported += 1
                        if not dry_run:
                            self.stdout.write(
                                self.style.SUCCESS(f"  ✓ Importada: {image_path.name} -> {title}")
                            )
                    else:
                        images_skipped += 1
            else:
                self.stdout.write(
                    self.style.WARNING("  ⚠ Directorio de imágenes scrapeadas no existe")
                )

        # Si se solicita asociar a noticias
        if associate_news:
            self.stdout.write("Asociando imágenes a NewsPage...\n")

            # Obtener todas las NewsPage
            news_pages = NewsPage.objects.all()

            for news_page in news_pages:
                # Si ya tiene imagen asociada, saltarla
                if news_page.featured_image and not dry_run:
                    continue

                found = False
                image_path = None

                # Estrategia 1: Buscar por palabras clave del título
                title_words = news_page.title.lower()
                # Extraer palabras significativas (más de 4 caracteres)
                keywords = [w for w in title_words.split() if len(w) > 4]
                # También buscar por palabras del slug
                slug_parts = [p for p in news_page.slug.split('-') if len(p) > 4]

                # Combinar keywords y slug_parts
                search_terms = list(set(keywords[:5] + slug_parts[:5]))  # Máximo 5 términos

                if images_dir.exists():
                    for term in search_terms:
                        # Buscar imágenes que contengan el término
                        for ext in ['.jpg', '.jpeg', '.png', '.gif']:
                            pattern = f"*{term}*{ext}"
                            matches = list(images_dir.glob(pattern))
                            if matches:
                                # Preferir imágenes sin sufijos numéricos múltiples
                                matches.sort(key=lambda x: (
                                    x.name.count('_'),
                                    x.name.count('-'),
                                    len(x.name)
                                ))
                                image_path = matches[0]
                                break
                        if image_path:
                            break

                # Estrategia 2: Buscar imágenes relacionadas con palabras específicas conocidas
                if not image_path:
                    # Mapeo de palabras clave comunes a nombres de archivos
                    title_lower = news_page.title.lower()
                    if 'elena' in title_lower or 'malvina' in title_lower:
                        for pattern in ['*Elena*', '*Malvina*', '*elena*', '*malvina*']:
                            matches = list(images_dir.glob(f"{pattern}.jpg")) + \
                                      list(images_dir.glob(f"{pattern}.jpeg")) + \
                                      list(images_dir.glob(f"{pattern}.png"))
                            if matches:
                                image_path = matches[0]
                                break
                    elif 'luis de pablo' in title_lower or 'luis-de-pablo' in title_lower:
                        for pattern in ['*Luis-de-Pablo*', '*luis-de-pablo*', '*Luis*Pablo*']:
                            matches = list(images_dir.glob(f"{pattern}.jpg")) + \
                                      list(images_dir.glob(f"{pattern}.jpeg")) + \
                                      list(images_dir.glob(f"{pattern}.png"))
                            if matches:
                                image_path = matches[0]
                                break
                    elif 'prado' in title_lower or 'micrologus' in title_lower:
                        for pattern in ['*Prado*', '*prado*', '*Micrologus*', '*micrologus*', '*MNP*', '*mnp*']:
                            matches = list(images_dir.glob(f"{pattern}.jpg")) + \
                                      list(images_dir.glob(f"{pattern}.jpeg")) + \
                                      list(images_dir.glob(f"{pattern}.png"))
                            if matches:
                                image_path = matches[0]
                                break
                    elif 'offenbach' in title_lower:
                        for pattern in ['*Offenbach*', '*offenbach*']:
                            matches = list(images_dir.glob(f"{pattern}.jpg")) + \
                                      list(images_dir.glob(f"{pattern}.jpeg")) + \
                                      list(images_dir.glob(f"{pattern}.png"))
                            if matches:
                                image_path = matches[0]
                                break
                    elif 'patrimonio' in title_lower:
                        for pattern in ['*Patrimonio*', '*patrimonio*']:
                            matches = list(images_dir.glob(f"{pattern}.jpg")) + \
                                      list(images_dir.glob(f"{pattern}.jpeg")) + \
                                      list(images_dir.glob(f"{pattern}.png"))
                            if matches:
                                image_path = matches[0]
                                break
                    elif 'barbara' in title_lower or 'braganza' in title_lower:
                        for pattern in ['*Barbara*', '*barbara*', '*Braganza*', '*braganza*', '*Maria-Barbara*']:
                            matches = list(images_dir.glob(f"{pattern}.jpg")) + \
                                      list(images_dir.glob(f"{pattern}.jpeg")) + \
                                      list(images_dir.glob(f"{pattern}.png"))
                            if matches:
                                image_path = matches[0]
                                break

                if image_path:
                    if self.associate_image_to_news(
                        news_page, image_path.name, images_dir, static_dir, dry_run
                    ):
                        found = True
                        news_associated += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  ✓ Asociada: {news_page.title} <- {image_path.name}"
                            )
                        )
                elif not dry_run:
                    self.stdout.write(
                        self.style.WARNING(f"  ⚠ No se encontró imagen para: {news_page.title}")
                    )

        # Importar imágenes destacadas desde Entrada
        self.stdout.write("\nImportando imágenes destacadas desde Entrada...\n")

        entradas = Entrada.objects.exclude(imagen_destacada__isnull=True).exclude(imagen_destacada='')
        for entrada in entradas:
            if entrada.imagen_destacada:
                # La imagen ya está en media/, solo crear registro en Wagtail
                image_path = entrada.imagen_destacada.path
                if os.path.exists(image_path):
                    wagtail_image = self.import_image_to_wagtail(
                        Path(image_path),
                        title=f"{entrada.titulo} - Imagen destacada",
                        dry_run=dry_run
                    )
                    if wagtail_image:
                        images_imported += 1

        # Resumen
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("RESUMEN:"))
        if dry_run:
            self.stdout.write("  [DRY-RUN] Simulación completada")
        self.stdout.write(f"  Imágenes importadas: {images_imported}")
        self.stdout.write(f"  Noticias asociadas: {news_associated}")
        self.stdout.write(f"  Imágenes omitidas: {images_skipped}")
        self.stdout.write("=" * 80)

