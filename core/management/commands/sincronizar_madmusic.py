"""
Management command para sincronizar contenido de Madmusic con el sitio original
Compara cada URL y actualiza el contenido si es necesario
"""
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

from core.models import Pagina, Proyecto


def normalize_url(slug):
    """Convertir slug a URL del sitio original"""
    base_url = "https://madmusic.iccmu.es"
    if slug == "proyecto-madmusic":
        return f"{base_url}/proyecto-madmusic/"
    return f"{base_url}/{slug}/"


def extract_content_from_html(html_content):
    """Extraer título y contenido principal del HTML"""
    soup = BeautifulSoup(html_content, "html.parser")

    # Extraer título - buscar primero en section#tools > h1
    titulo = None
    main_section = soup.find("section", id="tools")
    if main_section:
        h1 = main_section.find("h1")
        if h1:
            titulo = h1.get_text(strip=True)
    
    # Si no hay h1 en section#tools, buscar en otros lugares
    if not titulo:
        for selector in ["section#tools h1", "h1", ".entry-title", "title"]:
            elem = soup.select_one(selector)
            if elem:
                titulo = elem.get_text(strip=True)
                # Limpiar título - remover "ICCMU" o partes innecesarias
                titulo = re.sub(r"\s*\|\s*ICCMU.*$", "", titulo, flags=re.IGNORECASE)
                titulo = re.sub(r"^.*\|\s*", "", titulo)  # Remover todo antes de |
                titulo = re.sub(r"\s+", " ", titulo)
                if len(titulo) > 200:
                    titulo = titulo[:200]
                if titulo and titulo not in ["ICCMU", "Instituto Complutensede Ciencias Musicales"]:
                    break

    if not titulo or titulo in ["ICCMU", "Instituto Complutensede Ciencias Musicales"]:
        titulo = "Página"

    # Extraer contenido principal - buscar en section#tools
    contenido = None
    main_section = soup.find("section", id="tools")
    
    if main_section:
        # Buscar el div con el contenido principal (col-md-9)
        # El sitio usa Bootstrap: col-md-3 para sidebar, col-md-9 para contenido principal
        content_col = None
        
        # Buscar primero por col-md-9 (columna principal de contenido)
        # Buscar dentro de section#tools, pero asegurarse de que no incluya contenedores padre
        for div in main_section.find_all("div", recursive=True):
            classes = div.get('class', [])
            if not classes:
                continue
            classes_str = ' '.join(classes)
            # Buscar col-md-9 pero NO col-md-3 (sidebar)
            # Y asegurarse de que no sea hijo de un sidebar
            parent_classes = []
            parent = div.parent
            while parent and hasattr(parent, 'get'):
                if parent.get('class'):
                    parent_classes.extend(parent.get('class', []))
                parent = parent.parent if hasattr(parent, 'parent') else None
            
            parent_str = ' '.join(parent_classes)
            if ('col-md-9' in classes_str or 'col-md-8' in classes_str or 'col-md-10' in classes_str) and \
               'col-md-3' not in classes_str and 'sidebar' not in classes_str.lower() and \
               'sidebar' not in parent_str.lower() and 'col-md-3' not in parent_str:
                content_col = div
                break
        
        # Si encontramos el div de contenido, extraer solo su contenido interno
        if content_col:
            # Extraer el contenido interno del div col-md-9 usando decode_contents()
            # Esto extrae solo los hijos del div, sin incluir el div mismo ni sus hermanos
            try:
                inner_content = content_col.decode_contents()
            except:
                # Fallback: extraer hijos manualmente
                inner_content = ''.join(str(c) for c in content_col.children if (hasattr(c, 'name') and c.name) or (isinstance(c, str) and c.strip()))
            
            # Limpiar el contenido interno usando BeautifulSoup
            if inner_content:
                inner_soup = BeautifulSoup(inner_content, "html.parser")
                
                # Remover elementos no deseados
                for elem in inner_soup.find_all(["script", "style", "nav", "header", "footer", "form", "aside"]):
                    elem.decompose()
                
                # Remover cualquier sidebar que pueda estar dentro
                for sidebar in inner_soup.find_all(class_=lambda x: x and any(c in ' '.join(x) for c in ["sidebar", "parent_sidebar", "menu-principal-container", "col-md-3"])):
                    sidebar.decompose()
                
                contenido = str(inner_soup)
            else:
                # Si no hay contenido interno, usar el div completo pero sin clases Bootstrap
                content_col.attrs.pop('class', None)
                content_col.attrs.pop('id', None)
                contenido = str(content_col)
        else:
            # Si no encontramos col-md-9, buscar article
            article = main_section.find("article")
            if article:
                # Remover sidebars del article
                for sidebar in article.find_all(class_=lambda x: x and any(c in x for c in ["sidebar", "parent_sidebar", "menu-principal-container", "col-md-3"])):
                    sidebar.decompose()
                contenido = str(article)
            else:
                # Último recurso: remover explícitamente el sidebar de section#tools
                # Buscar y remover el div con col-md-3 (sidebar)
                for sidebar_div in main_section.find_all("div", class_=lambda x: x and any(c in x for c in ["col-md-3", "parent_sidebar", "sidebar"])):
                    sidebar_div.decompose()
                # Remover otros elementos no deseados
                for elem in main_section.find_all(["script", "style", "nav", "header", "footer", "form"]):
                    elem.decompose()
                contenido = str(main_section)
    
    # Si no hay section#tools, buscar en article o main
    if not contenido:
        article = soup.find("article") or soup.find("main")
        if article:
            # Remover sidebars y menús
            for elem in article.find_all([
                "script", "style", "nav", "header", "footer", "form",
                "aside", ".sidebar", "#sidebar", ".menu", ".widget",
                ".parent_sidebar", "#sidebar_menu_container"
            ]):
                elem.decompose()
            contenido = str(article)

    if contenido:
        # Limpiar contenedores innecesarios usando BeautifulSoup
        contenido_soup = BeautifulSoup(contenido, "html.parser")
        
        # Remover <main> si existe
        for main in contenido_soup.find_all("main"):
            # Reemplazar main con su contenido interno
            main.replace_with(*main.children)
        
        # Remover <section id="page"> si existe
        for section in contenido_soup.find_all("section", id="page"):
            section.replace_with(*list(section.children))
        
        # Remover sidebars completos
        for sidebar in contenido_soup.find_all(class_=lambda x: x and any(c in ' '.join(x) for c in ["parent_sidebar", "col-md-3", "sidebar_menu_container"])):
            sidebar.decompose()
        
        # Buscar y extraer solo el contenido de col-md-9 (sin sidebar)
        content_col = contenido_soup.find("div", class_=lambda x: x and "col-md-9" in ' '.join(x) if x else False)
        
        if content_col:
            # Extraer el contenido interno del col-md-9 usando decode_contents
            try:
                inner_html = content_col.decode_contents()
            except:
                inner_html = ''.join(str(c) for c in content_col.children if (hasattr(c, 'name') and c.name) or (isinstance(c, str) and c.strip()))
            
            # Limpiar el HTML interno
            inner_soup = BeautifulSoup(inner_html, "html.parser")
            
            # Remover breadcrumbs
            for breadcrumb in inner_soup.find_all(class_=lambda x: x and "breadcrumb" in ' '.join(x).lower() if x else False):
                breadcrumb.decompose()
            
            # Remover cualquier sidebar
            for sidebar in inner_soup.find_all(class_=lambda x: x and any(c in ' '.join(x) for c in ["parent_sidebar", "col-md-3", "sidebar_menu", "sidebar"])):
                sidebar.decompose()
            
            # Buscar el div con class="content" que contiene el contenido real
            content_div = inner_soup.find("div", class_="content")
            if content_div:
                # Extraer solo el contenido interno del div.content (sin el wrapper)
                content_inner = content_div.decode_contents() if hasattr(content_div, 'decode_contents') else ''.join(str(c) for c in content_div.children)
                contenido_soup = BeautifulSoup(content_inner, "html.parser")
            else:
                contenido_soup = inner_soup
        
        # Limpieza final: remover cualquier sidebar que pueda quedar usando regex
        contenido = str(contenido_soup)
        
        # Remover divs con sidebar usando regex (más agresivo y múltiples pasadas)
        # Patrón para divs con sidebar (puede tener múltiples líneas)
        contenido = re.sub(r'<div[^>]*class="[^"]*parent_sidebar[^"]*"[^>]*>.*?</div>\s*', '', contenido, flags=re.DOTALL | re.IGNORECASE)
        contenido = re.sub(r'<div[^>]*class="[^"]*col-md-3[^"]*"[^>]*>.*?</div>\s*', '', contenido, flags=re.DOTALL | re.IGNORECASE)
        contenido = re.sub(r'<div[^>]*id="sidebar[^"]*"[^>]*>.*?</div>\s*', '', contenido, flags=re.DOTALL | re.IGNORECASE)
        
        # Remover contenedores que solo tienen sidebar
        contenido = re.sub(r'<div[^>]*class="[^"]*container[^"]*"[^>]*>\s*<div[^>]*class="[^"]*row[^"]*"[^>]*>\s*<!--\s*Sidebar\s*-->.*?</div>\s*</div>', '', contenido, flags=re.DOTALL | re.IGNORECASE)
        
        # Remover comentarios de sidebar
        contenido = re.sub(r'<!--\s*Sidebar\s*-->', '', contenido, flags=re.IGNORECASE)
        
        # Si después de limpiar todavía tiene sidebar, hacer una limpieza más agresiva
        if 'parent_sidebar' in contenido.lower() or 'col-md-3' in contenido:
            # Buscar el div con class="content" que debería tener el contenido real
            temp_soup = BeautifulSoup(contenido, "html.parser")
            content_div = temp_soup.find("div", class_="content")
            if content_div:
                contenido = str(content_div)
            else:
                # Si no hay div.content, buscar cualquier div que tenga texto útil pero no sidebar
                for div in temp_soup.find_all("div"):
                    div_text = div.get_text(strip=True)
                    div_classes = ' '.join(div.get('class', []))
                    if len(div_text) > 200 and 'sidebar' not in div_classes.lower() and 'col-md-3' not in div_classes:
                        contenido = str(div)
                        break
        
        # Limpieza final: buscar y extraer solo el contenido dentro del div con class="content"
        final_soup = BeautifulSoup(contenido, "html.parser")
        content_div_final = final_soup.find("div", class_="content")
        if content_div_final:
            # Extraer solo el contenido interno (párrafos, listas, etc.) sin el wrapper div
            try:
                inner_content = content_div_final.decode_contents()
                # Si el contenido interno tiene suficiente texto, usarlo directamente
                if len(inner_content.strip()) > 50:
                    contenido = inner_content
                else:
                    contenido = str(content_div_final)
            except:
                # Si decode_contents falla, extraer hijos manualmente
                inner_parts = []
                for child in content_div_final.children:
                    if hasattr(child, 'name') and child.name:
                        inner_parts.append(str(child))
                    elif isinstance(child, str) and child.strip():
                        inner_parts.append(child)
                if inner_parts:
                    contenido = ''.join(inner_parts)
                else:
                    contenido = str(content_div_final)
        else:
            # Remover breadcrumbs si existen
            for breadcrumb in final_soup.find_all(class_=lambda x: x and "breadcrumb" in ' '.join(x).lower() if x else False):
                breadcrumb.decompose()
            # Remover wrappers innecesarios de Bootstrap
            for wrapper in final_soup.find_all("div", class_=lambda x: x and any(c in ' '.join(x) for c in ["col-md-12", "col-md-9", "row"]) if x else False):
                # Si el wrapper solo contiene contenido útil, extraerlo
                wrapper_text = wrapper.get_text(strip=True)
                if len(wrapper_text) > 100:
                    try:
                        contenido = wrapper.decode_contents()
                        break
                    except:
                        pass
            if not contenido or len(contenido.strip()) < 100:
                contenido = str(final_soup)
        
        # Limpiar y normalizar URLs
        # Convertir URLs absolutas del sitio original a relativas
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
        # Limpiar URLs relativas que puedan tener problemas
        # Pero evitar duplicar /madmusic/
        contenido = re.sub(
            r'href="/(?!madmusic/)([^"]+)"',
            r'href="/madmusic/\1"',
            contenido
        )
        # Corregir URLs duplicadas /madmusic/madmusic/
        contenido = re.sub(
            r'href="/madmusic/madmusic/',
            r'href="/madmusic/',
            contenido
        )
        # Limitar tamaño si es muy grande
        if len(contenido) > 200000:
            contenido = contenido[:200000] + "..."
    else:
        contenido = "<p>Contenido de la página</p>"

    return titulo, contenido


class Command(BaseCommand):
    help = "Sincroniza contenido de Madmusic comparando con el sitio original"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Forzar actualización incluso si el contenido parece correcto",
        )
        parser.add_argument(
            "--slug",
            type=str,
            help="Sincronizar solo una página específica por slug",
        )
        parser.add_argument(
            "--limit",
            type=int,
            help="Limitar el número de páginas a sincronizar (útil para pruebas)",
        )

    def handle(self, *args, **options):
        force = options["force"]
        slug_filter = options.get("slug")

        # Obtener proyecto
        proyecto = Proyecto.objects.filter(slug="madmusic").first()
        if not proyecto:
            self.stdout.write(
                self.style.ERROR("Proyecto 'madmusic' no encontrado. Ejecuta primero: python manage.py poblar_madmusic_rapido")
            )
            return

        # Obtener páginas a sincronizar
        if slug_filter:
            paginas = Pagina.objects.filter(slug=slug_filter, proyecto=proyecto)
        else:
            paginas = Pagina.objects.filter(proyecto=proyecto).order_by("slug")
        
        # Aplicar límite si se especifica
        limit = options.get("limit")
        if limit:
            paginas = paginas[:limit]

        if not paginas.exists():
            self.stdout.write(self.style.ERROR("No se encontraron páginas para sincronizar"))
            return

        total_paginas = paginas.count()
        self.stdout.write(f"\n{'='*80}")
        self.stdout.write(f"Sincronizando {total_paginas} página(s)...")
        self.stdout.write(f"{'='*80}\n")

        actualizadas = 0
        errores = 0
        sin_cambios = 0
        total_paginas = paginas.count()

        for idx, pagina in enumerate(paginas, 1):
            self.stdout.write(f"[{idx}/{total_paginas}] ", ending='')
            url_original = normalize_url(pagina.slug)
            
            self.stdout.write(f"\n📄 {pagina.slug}")
            self.stdout.write(f"   URL original: {url_original}")
            self.stdout.write(f"   URL local: /madmusic/{pagina.slug}/")

            try:
                # Hacer request al sitio original con timeout más corto
                response = requests.get(url_original, timeout=5, allow_redirects=True)
                
                if response.status_code == 404:
                    self.stdout.write(
                        self.style.WARNING(f"   ⚠️  No encontrada en sitio original (404)")
                    )
                    errores += 1
                    continue

                if response.status_code != 200:
                    self.stdout.write(
                        self.style.WARNING(f"   ⚠️  Error HTTP {response.status_code}")
                    )
                    errores += 1
                    continue

                # Extraer contenido
                titulo_nuevo, contenido_nuevo = extract_content_from_html(response.text)

                # Verificar si hay cambios significativos
                contenido_actual = pagina.cuerpo or ""
                titulo_actual = pagina.titulo or ""

                # Comparar contenido (solo si no es force)
                if not force:
                    # Si el contenido actual es muy corto o parece placeholder, actualizar
                    if len(contenido_actual) < 500 or "Contenido de la página" in contenido_actual:
                        necesita_actualizar = True
                    # Si el título es muy genérico, actualizar
                    elif titulo_actual == "Instituto Complutensede Ciencias Musicales" or len(titulo_actual) < 10:
                        necesita_actualizar = True
                    else:
                        # Comparar longitudes (si difieren mucho, puede haber cambios)
                        diferencia_longitud = abs(len(contenido_nuevo) - len(contenido_actual))
                        if diferencia_longitud > len(contenido_actual) * 0.3:  # Más del 30% de diferencia
                            necesita_actualizar = True
                        else:
                            necesita_actualizar = False
                else:
                    necesita_actualizar = True

                if necesita_actualizar:
                    pagina.titulo = titulo_nuevo
                    pagina.cuerpo = contenido_nuevo
                    pagina.proyecto = proyecto
                    pagina.save()
                    actualizadas += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"   ✓ Actualizada (Título: {titulo_nuevo[:50]}...)")
                    )
                else:
                    sin_cambios += 1
                    self.stdout.write(f"   - Sin cambios necesarios")

            except requests.exceptions.RequestException as e:
                self.stdout.write(
                    self.style.ERROR(f"   ✗ Error al obtener contenido: {e}")
                )
                errores += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"   ✗ Error inesperado: {e}")
                )
                errores += 1

        # Resumen
        self.stdout.write(f"\n{'='*80}")
        self.stdout.write(self.style.SUCCESS("RESUMEN:"))
        self.stdout.write(f"  ✓ Actualizadas: {actualizadas}")
        self.stdout.write(f"  - Sin cambios: {sin_cambios}")
        self.stdout.write(f"  ✗ Errores: {errores}")
        self.stdout.write(f"{'='*80}\n")




