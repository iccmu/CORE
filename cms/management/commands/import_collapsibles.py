"""
Comando Django management para importar acordeones desde el JSON extraído
a las páginas de Wagtail correspondientes.

Uso:
    python manage.py import_collapsibles [--dry-run] [--page-slug SLUG]
"""

import json
import re
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from bs4 import BeautifulSoup

from cms.models import StandardPage


class Command(BaseCommand):
    help = 'Importa acordeones desde collapsibles.json a páginas de Wagtail'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar lo que se haría sin modificar la base de datos',
        )
        parser.add_argument(
            '--page-slug',
            type=str,
            help='Importar solo una página específica por su slug',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Sobrescribir contenido existente',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        page_slug = options.get('page_slug')
        force = options['force']
        
        # Cargar el JSON con los acordeones extraídos
        json_path = Path(__file__).parent.parent.parent.parent / 'data' / 'collapsibles.json'
        
        if not json_path.exists():
            raise CommandError(f'No se encontró el archivo {json_path}')
        
        with open(json_path, 'r', encoding='utf-8') as f:
            collapsibles_data = json.load(f)
        
        # Mapeo de archivos HTML a slugs de páginas
        # Basado en las páginas existentes en la base de datos
        page_mapping = {
            'servicios-e-infraestructura': 'servicios-e-infraestructura',
            'transferencia_exposiciones': 'exposiciones',
            'transferencia_conciertos': 'conciertos',
            'proyecto-madmusic_objetivos': 'objetivos',
            'proyecto-madmusic_investigacion': 'investigacion',
            'formacion-empleo_empleo': 'empleo',
            'equipo_participantes': 'participantes',
            'equipo_grupos-beneficiarios': 'grupos-beneficiarios',
            'equipo': 'equipo',
            'divulgacion-cientifica_publicaciones-madmusic-2': 'publicaciones-madmusic-2',
            'divulgacion-cientifica_cuadernos-de-musica-iberoamericana': 'cuadernos-de-musica-iberoamericana',
            'divulgacion-cientifica_congresos-madmusic': 'congresos-madmusic',
            'divulgacion-cientifica_articulos-en-revistas-cientificas': 'articulos-en-revistas-cientificas',
            'divulgacion-cientifica_archivos': 'archivos',
            'cursos-de-verano': 'cursos-de-verano',
        }
        
        self.stdout.write(self.style.SUCCESS(f'\n🎯 Importando acordeones {"(DRY RUN)" if dry_run else ""}'))
        self.stdout.write(f'📊 Total de páginas con acordeones: {len(collapsibles_data)}\n')
        
        imported = 0
        skipped = 0
        errors = 0
        
        for page_key, page_data in collapsibles_data.items():
            # Si se especificó una página, solo procesar esa
            if page_slug and page_mapping.get(page_key) != page_slug:
                continue
            
            target_slug = page_mapping.get(page_key)
            if not target_slug:
                self.stdout.write(self.style.WARNING(
                    f'⚠️  No hay mapeo para {page_key}, saltando...'
                ))
                skipped += 1
                continue
            
            self.stdout.write(f'\n📄 Procesando: {page_data["source_file"]}')
            self.stdout.write(f'   Slug objetivo: {target_slug}')
            self.stdout.write(f'   Acordeones: {page_data["accordion_count"]}')
            
            try:
                # Buscar la página por slug
                try:
                    page = StandardPage.objects.get(slug=target_slug)
                except StandardPage.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f'   ⚠️  Página no encontrada: {target_slug}'
                    ))
                    self.stdout.write(f'   💡 Puedes crearla primero en el admin de Wagtail')
                    skipped += 1
                    continue
                
                # Verificar si ya tiene contenido
                if page.body and not force:
                    self.stdout.write(self.style.WARNING(
                        f'   ⚠️  La página ya tiene contenido. Usa --force para sobrescribir'
                    ))
                    skipped += 1
                    continue
                
                # Construir el StreamField con los acordeones
                accordions_list = []
                for accordion in page_data['accordions']:
                    # Limpiar el HTML del contenido
                    content_html = self.clean_html_for_richtext(accordion['content_html'])
                    
                    # ListBlock no necesita el wrapper type/value
                    accordions_list.append({
                        'title': accordion['title'],
                        'content': content_html
                    })
                
                # Crear el bloque de grupo de acordeones
                stream_data = [{
                    'type': 'accordion_group',
                    'value': {
                        'heading': '',
                        'accordions': accordions_list,
                        'allow_multiple_open': False,
                        'first_accordion_open': False
                    }
                }]
                
                if not dry_run:
                    # Actualizar la página
                    page.body = stream_data
                    page.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS(
                        f'   ✅ Importados {len(accordions_list)} acordeones'
                    ))
                else:
                    self.stdout.write(f'   🔍 Se importarían {len(accordions_list)} acordeones')
                
                imported += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ❌ Error: {str(e)}'))
                errors += 1
        
        # Resumen final
        self.stdout.write(self.style.SUCCESS(f'\n✨ Importación completada!'))
        self.stdout.write(f'   ✅ Páginas actualizadas: {imported}')
        self.stdout.write(f'   ⏭️  Páginas saltadas: {skipped}')
        self.stdout.write(f'   ❌ Errores: {errors}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING(
                '\n💡 Esto fue un DRY RUN. Ejecuta sin --dry-run para aplicar cambios.'
            ))
    
    def clean_html_for_richtext(self, html_content: str) -> str:
        """
        Limpia el HTML del contenido del acordeón para que sea compatible
        con el RichTextField de Wagtail.
        
        Args:
            html_content: HTML crudo del acordeón
            
        Returns:
            HTML limpio compatible con Wagtail
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Encontrar el div.panel-body y extraer su contenido
        panel_body = soup.find('div', class_='panel-body')
        if not panel_body:
            return html_content
        
        # Obtener todo el contenido interno
        content = ''.join(str(child) for child in panel_body.children)
        
        # Limpiar espacios en blanco excesivos
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = content.strip()
        
        return content
