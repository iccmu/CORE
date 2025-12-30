"""
Comando para migrar datos de Madmusic desde core.models a Wagtail CMS.

Uso:
    python manage.py migrate_madmusic_to_wagtail --dry-run  # Simulación
    python manage.py migrate_madmusic_to_wagtail --apply     # Aplicar cambios
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from wagtail.models import Site, Page
from wagtail.contrib.redirects.models import Redirect
from core.models import Proyecto, Entrada, Pagina
from cms.models import HomePage, StandardPage, NewsIndexPage, NewsPage


class Command(BaseCommand):
    help = "Migra datos de Madmusic desde core.models a Wagtail CMS"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simular la migración sin aplicar cambios",
        )
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Aplicar la migración (requerido para hacer cambios)",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        apply = options["apply"]

        if not dry_run and not apply:
            self.stdout.write(
                self.style.ERROR(
                    "Debes especificar --dry-run o --apply"
                )
            )
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING("=== MODO DRY-RUN (simulación) ===\n")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("=== APLICANDO MIGRACIÓN ===\n")
            )

        # 1. Verificar proyecto madmusic
        proyecto = Proyecto.objects.filter(slug="madmusic").first()
        if not proyecto:
            self.stdout.write(
                self.style.WARNING(
                    "⚠ No se encontró el proyecto 'madmusic'. "
                    "La migración continuará pero no habrá datos para migrar."
                )
            )
            proyecto = None
        else:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Proyecto encontrado: {proyecto.titulo}")
            )

        entradas_count = Entrada.objects.filter(proyecto=proyecto).count() if proyecto else 0
        paginas_count = Pagina.objects.filter(proyecto=proyecto).count() if proyecto else 0

        self.stdout.write(f"  - Entradas: {entradas_count}")
        self.stdout.write(f"  - Páginas: {paginas_count}\n")

        # 2. Crear estructura base: HomePage y NewsIndexPage (PRIMERO)
        self.stdout.write("\n=== CREANDO ESTRUCTURA BASE ===")

        # Obtener el root page de Wagtail (depth=1)
        wagtail_root = Page.objects.filter(depth=1).first()
        
        if not wagtail_root:
            self.stdout.write(
                self.style.ERROR("⚠ No se encontró el root page de Wagtail")
            )
            return

        # Buscar o crear HomePage como hijo del root
        if dry_run:
            home_page = HomePage.objects.child_of(wagtail_root).filter(slug="madmusic-home").first()
            if home_page:
                self.stdout.write(f"  [DRY-RUN] HomePage existente: {home_page.title}")
                root_page = home_page
            else:
                self.stdout.write("  [DRY-RUN] Se crearía HomePage 'Madmusic Home'")
                # En dry-run, usar wagtail_root como root_page para evitar errores
                root_page = wagtail_root
        else:
            # Buscar si ya existe
            home_page = HomePage.objects.child_of(wagtail_root).filter(slug="madmusic-home").first()
            
            if not home_page:
                # Crear nueva HomePage
                home_page = HomePage(
                    title="Madmusic Home",
                    slug="madmusic-home",
                    intro="Bienvenido al proyecto Madmusic",
                )
                wagtail_root.add_child(instance=home_page)
                home_page.save_revision().publish()
                self.stdout.write(
                    self.style.SUCCESS("✓ HomePage 'Madmusic Home' creada")
                )
            else:
                self.stdout.write(f"✓ HomePage existente: {home_page.title}")
            
            root_page = home_page  # Usar home_page como root para las migraciones

        # 3. Crear/obtener Site de Wagtail (DESPUÉS de crear HomePage)
        self.stdout.write("\n=== CONFIGURANDO SITE DE WAGTAIL ===")
        site_hostname = "madmusic.iccmu.es"
        site_port = 80

        if dry_run:
            site = Site.objects.filter(hostname=site_hostname).first()
            if site:
                self.stdout.write(f"  [DRY-RUN] Site existente: {site_hostname}")
            else:
                self.stdout.write(f"  [DRY-RUN] Se crearía Site: {site_hostname}")
        else:
            # Crear Site con root_page si no existe
            site, created = Site.objects.get_or_create(
                hostname=site_hostname,
                port=site_port,
                defaults={
                    "site_name": "Madmusic",
                    "root_page": root_page,
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Site creado: {site_hostname}")
                )
            else:
                # Actualizar root_page si es necesario
                if site.root_page != root_page:
                    site.root_page = root_page
                    site.save()
                    self.stdout.write(f"✓ Site actualizado: {site_hostname}")
                else:
                    self.stdout.write(f"✓ Site existente: {site_hostname}")

        # Crear NewsIndexPage con slug "noticias"
        if dry_run:
            if root_page and hasattr(root_page, 'path'):
                news_index = NewsIndexPage.objects.child_of(root_page).filter(slug="noticias").first()
            else:
                news_index = None
            if news_index:
                self.stdout.write(f"  [DRY-RUN] NewsIndexPage 'noticias' existente")
            else:
                self.stdout.write("  [DRY-RUN] Se crearía NewsIndexPage 'noticias'")
                news_index = None  # Para evitar errores en dry-run
        else:
            # Buscar si ya existe
            news_index = NewsIndexPage.objects.child_of(root_page).filter(slug="noticias").first()
            
            if not news_index:
                # Crear nueva NewsIndexPage
                news_index = NewsIndexPage(
                    title="Noticias",
                    slug="noticias",
                    intro="Noticias del proyecto Madmusic",
                )
                root_page.add_child(instance=news_index)
                news_index.save_revision().publish()
                self.stdout.write(
                    self.style.SUCCESS("✓ NewsIndexPage 'noticias' creada")
                )
            else:
                self.stdout.write("✓ NewsIndexPage 'noticias' existente")

        # 4. Migrar Páginas → StandardPage
        self.stdout.write("\n=== MIGRANDO PÁGINAS → STANDARDPAGE ===")
        
        if proyecto:
            paginas = Pagina.objects.filter(proyecto=proyecto).order_by("slug")
            paginas_migradas = 0
            
            for pagina in paginas:
                self._migrate_pagina(pagina, root_page, dry_run)
                paginas_migradas += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ {paginas_migradas} páginas procesadas"
                )
            )
        else:
            self.stdout.write("  (No hay páginas para migrar)")

        # 5. Migrar Entradas → NewsPage
        self.stdout.write("\n=== MIGRANDO ENTRADAS → NEWSPAGE ===")
        
        if proyecto and news_index:
            entradas = Entrada.objects.filter(proyecto=proyecto).order_by("-fecha_publicacion")
            entradas_migradas = 0
            
            for entrada in entradas:
                self._migrate_entrada(entrada, news_index, dry_run)
                entradas_migradas += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ {entradas_migradas} entradas procesadas"
                )
            )
        else:
            if not proyecto:
                self.stdout.write("  (No hay entradas para migrar - proyecto no encontrado)")
            elif not news_index:
                self.stdout.write("  (No hay entradas para migrar - NewsIndexPage no creada)")

        # 6. Crear redirects 301
        self.stdout.write("\n=== CREANDO REDIRECTS 301 ===")
        
        if proyecto:
            redirects_count = self._create_redirects(proyecto, dry_run)
            self.stdout.write(
                self.style.SUCCESS(f"✓ {redirects_count} redirects procesados")
            )
        else:
            self.stdout.write("  (No hay redirects para crear)")

        self.stdout.write("\n" + "=" * 50)
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "DRY-RUN completado. Usa --apply para aplicar los cambios."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("Migración completada exitosamente!")
            )

    def _migrate_pagina(self, pagina, root_page, dry_run):
        """Migra una Pagina a StandardPage respetando jerarquía de slugs"""
        slug_parts = pagina.slug.split("/")
        slug_parts = [s for s in slug_parts if s]  # Eliminar vacíos
        
        if not slug_parts:
            self.stdout.write(
                self.style.WARNING(f"  ⚠ Slug vacío para página: {pagina.titulo}")
            )
            return

        # Construir jerarquía de páginas padre
        current_parent = root_page
        created_pages = []
        
        # Crear páginas padre si no existen (excepto la última que es la página real)
        for i, slug_part in enumerate(slug_parts[:-1]):
            parent_slug = slug_part
            
            if dry_run:
                existing = StandardPage.objects.child_of(current_parent).filter(slug=parent_slug).first()
                if existing:
                    current_parent = existing
                    self.stdout.write(f"  [DRY-RUN] Padre existente: {current_parent.url_path}")
                else:
                    self.stdout.write(f"  [DRY-RUN] Se crearía padre: {parent_slug}")
                    # Simular creación
                    created_pages.append(parent_slug)
            else:
                # Buscar si ya existe
                parent_page = StandardPage.objects.child_of(current_parent).filter(slug=parent_slug).first()
                
                if not parent_page:
                    # Crear nueva página padre
                    parent_page = StandardPage(
                        title=parent_slug.replace("-", " ").title(),
                        slug=parent_slug,
                        body="<p>Página contenedora creada automáticamente durante la migración.</p>",
                    )
                    current_parent.add_child(instance=parent_page)
                    parent_page.save_revision().publish()
                    created_pages.append(parent_slug)
                
                current_parent = parent_page

        # Crear/actualizar la página final
        final_slug = slug_parts[-1]
        
        if dry_run:
            existing = StandardPage.objects.child_of(current_parent).filter(slug=final_slug).first()
            if existing:
                self.stdout.write(
                    f"  [DRY-RUN] Página existente: {pagina.titulo} → {existing.url_path}"
                )
            else:
                self.stdout.write(
                    f"  [DRY-RUN] Se crearía: {pagina.titulo} → {current_parent.url_path}{final_slug}/"
                )
        else:
            # Buscar si ya existe
            existing = StandardPage.objects.child_of(current_parent).filter(slug=final_slug).first()
            
            # Convertir HTML a RichText (Wagtail lo maneja automáticamente)
            body_content = pagina.cuerpo if pagina.cuerpo else "<p></p>"
            
            if existing:
                # Actualizar si ya existe
                existing.title = pagina.titulo
                existing.body = body_content
                existing.save()
                existing.save_revision().publish()
                self.stdout.write(
                    f"  ✓ Actualizada: {pagina.titulo} → {existing.url_path}"
                )
            else:
                # Crear nueva página
                page = StandardPage(
                    title=pagina.titulo,
                    slug=final_slug,
                    body=body_content,
                )
                current_parent.add_child(instance=page)
                page.save_revision().publish()
                self.stdout.write(
                    f"  ✓ Creada: {pagina.titulo} → {page.url_path}"
                )

    def _migrate_entrada(self, entrada, news_index, dry_run):
        """Migra una Entrada a NewsPage bajo NewsIndexPage"""
        slug = entrada.slug
        
        if dry_run:
            existing = NewsPage.objects.child_of(news_index).filter(slug=slug).first()
            if existing:
                self.stdout.write(
                    f"  [DRY-RUN] Noticia existente: {entrada.titulo} → {existing.url_path}"
                )
            else:
                self.stdout.write(
                    f"  [DRY-RUN] Se crearía: {entrada.titulo} → /noticias/{slug}/"
                )
        else:
            # Buscar si ya existe
            existing = NewsPage.objects.child_of(news_index).filter(slug=slug).first()
            
            # Convertir HTML a RichText
            body_content = entrada.cuerpo if entrada.cuerpo else "<p></p>"
            intro_content = entrada.resumen[:250] if entrada.resumen else ""
            
            if existing:
                # Actualizar si ya existe
                existing.title = entrada.titulo
                existing.date = entrada.fecha_publicacion
                existing.intro = intro_content
                existing.body = body_content
                existing.save()
                news_page = existing
            else:
                # Crear nueva NewsPage
                news_page = NewsPage(
                    title=entrada.titulo,
                    slug=slug,
                    date=entrada.fecha_publicacion,
                    intro=intro_content,
                    body=body_content,
                )
                news_index.add_child(instance=news_page)
            
            # Publicar con fecha original
            revision = news_page.save_revision()
            if entrada.fecha_publicacion:
                news_page.first_published_at = timezone.make_aware(
                    timezone.datetime.combine(entrada.fecha_publicacion, timezone.datetime.min.time())
                )
            revision.publish()
            
            if existing:
                self.stdout.write(
                    f"  ✓ Actualizada: {entrada.titulo} → {news_page.url_path}"
                )
            else:
                self.stdout.write(
                    f"  ✓ Creada: {entrada.titulo} → {news_page.url_path}"
                )

    def _create_redirects(self, proyecto, dry_run):
        """Crea redirects 301 para URLs antiguas de entradas"""
        from urllib.parse import urlparse
        
        entradas = Entrada.objects.filter(proyecto=proyecto)
        redirects_count = 0
        site = Site.objects.filter(hostname="madmusic.iccmu.es").first()
        
        if not site:
            self.stdout.write(
                self.style.WARNING("  ⚠ No se encontró el site para crear redirects")
            )
            return 0
        
        for entrada in entradas:
            # Determinar old_path
            # Prioridad: url_original si existe y es fiable, sino usar /<slug>/
            old_path = None
            
            if entrada.url_original:
                # Extraer path de la URL
                parsed = urlparse(entrada.url_original)
                if parsed.path:
                    old_path = parsed.path
                    # Asegurar que empiece con /
                    if not old_path.startswith("/"):
                        old_path = "/" + old_path
                    # Eliminar trailing slash para consistencia
                    old_path = old_path.rstrip("/")
            
            # Si no hay url_original o no es válida, usar /<slug>/
            if not old_path:
                old_path = f"/{entrada.slug}/"
            
            # new_path siempre es /noticias/<slug>/
            new_path = f"/noticias/{entrada.slug}/"
            
            if dry_run:
                existing = Redirect.objects.filter(old_path=old_path, site=site).first()
                if existing:
                    redirect_target = existing.redirect_page.url_path if existing.redirect_page else existing.link
                    self.stdout.write(
                        f"  [DRY-RUN] Redirect existente: {old_path} → {redirect_target}"
                    )
                else:
                    self.stdout.write(
                        f"  [DRY-RUN] Se crearía redirect: {old_path} → {new_path}"
                    )
                redirects_count += 1
            else:
                # Buscar la NewsPage correspondiente
                news_index = NewsIndexPage.objects.filter(slug="noticias").first()
                if news_index:
                    news_page = NewsPage.objects.child_of(news_index).filter(slug=entrada.slug).first()
                    
                    if news_page:
                        redirect, created = Redirect.objects.get_or_create(
                            old_path=old_path,
                            site=site,
                            defaults={
                                "redirect_page": news_page,
                                "is_permanent": True,
                            },
                        )
                        if created:
                            redirects_count += 1
                            self.stdout.write(
                                f"  ✓ Redirect: {old_path} → {new_path}"
                            )

        return redirects_count

