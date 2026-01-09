#!/usr/bin/env python3
"""
Script para extraer contenido de acordeones Bootstrap del HTML scrapeado de madmusic.iccmu.es

Este script:
1. Lee los archivos HTML del directorio scraped_madmusic/html/
2. Extrae todos los acordeones (elementos con class="panel-collapse collapse")
3. Genera un JSON estructurado con el contenido
4. Preserva el HTML interno completo
"""

import json
import os
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Dict, List, Any


def extract_accordions_from_html(html_path: str) -> List[Dict[str, Any]]:
    """
    Extrae todos los acordeones de un archivo HTML.
    
    Args:
        html_path: Ruta al archivo HTML
        
    Returns:
        Lista de diccionarios con la información de cada acordeón
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    accordions = []
    
    # Buscar todos los paneles con acordeones
    panels = soup.find_all('div', class_='panel')
    
    for panel in panels:
        # Buscar el heading (título clickeable)
        heading = panel.find('div', class_='panel-heading')
        if not heading:
            continue
            
        title_elem = heading.find('h4', class_='panel-title')
        if not title_elem:
            continue
        
        # Extraer el título (puede estar dentro de un <a>)
        title_link = title_elem.find('a')
        if title_link:
            # Remover espacios en blanco excesivos y saltos de línea
            title = ' '.join(title_link.get_text(strip=True).split())
        else:
            title = ' '.join(title_elem.get_text(strip=True).split())
        
        # Buscar el contenido colapsable
        collapse = panel.find('div', class_='panel-collapse')
        if not collapse:
            continue
        
        # Extraer el ID del collapse para mantener la estructura
        collapse_id = collapse.get('id', '')
        
        # Buscar el cuerpo del panel
        body = collapse.find('div', class_='panel-body')
        if not body:
            continue
        
        # Extraer el contenido HTML completo del body
        content_html = str(body)
        
        # También extraer el texto plano para referencia
        content_text = body.get_text(strip=True)
        
        accordion_data = {
            'title': title,
            'collapse_id': collapse_id,
            'content_html': content_html,
            'content_text': content_text[:200] + '...' if len(content_text) > 200 else content_text,  # Preview
            'has_images': bool(body.find_all('img')),
            'has_links': bool(body.find_all('a')),
            'has_lists': bool(body.find_all(['ul', 'ol']))
        }
        
        accordions.append(accordion_data)
    
    return accordions


def main():
    """Función principal que procesa todos los archivos HTML."""
    
    # Configurar rutas
    base_dir = Path(__file__).parent.parent
    html_dir = base_dir / 'scraped_madmusic' / 'html'
    output_dir = base_dir / 'data'
    output_dir.mkdir(exist_ok=True)
    
    # Archivos HTML que contienen acordeones (basado en el análisis previo)
    html_files = [
        'servicios-e-infraestructura.html',
        'transferencia/exposiciones.html',
        'transferencia/conciertos.html',
        'proyecto-madmusic/objetivos.html',
        'proyecto-madmusic/investigacion.html',
        'formacion-empleo/empleo.html',
        'equipo/participantes.html',
        'equipo/grupos-beneficiarios.html',
        'equipo.html',
        'divulgacion-cientifica/publicaciones-madmusic-2.html',
        'divulgacion-cientifica/cuadernos-de-musica-iberoamericana.html',
        'divulgacion-cientifica/congresos-madmusic.html',
        'divulgacion-cientifica/articulos-en-revistas-cientificas.html',
        'divulgacion-cientifica/archivos.html',
        'cursos-de-verano.html',
    ]
    
    all_data = {}
    total_accordions = 0
    
    print("🔍 Extrayendo acordeones del HTML scrapeado...\n")
    
    for html_file in html_files:
        html_path = html_dir / html_file
        
        if not html_path.exists():
            print(f"⚠️  Archivo no encontrado: {html_file}")
            continue
        
        print(f"📄 Procesando: {html_file}")
        accordions = extract_accordions_from_html(str(html_path))
        
        if accordions:
            # Limpiar el nombre del archivo para usarlo como key
            page_key = html_file.replace('.html', '').replace('/', '_')
            all_data[page_key] = {
                'source_file': html_file,
                'accordion_count': len(accordions),
                'accordions': accordions
            }
            total_accordions += len(accordions)
            print(f"   ✅ Extraídos {len(accordions)} acordeones")
        else:
            print(f"   ⚠️  No se encontraron acordeones")
    
    # Guardar el JSON
    output_file = output_dir / 'collapsibles.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✨ Extracción completada!")
    print(f"📊 Total de páginas procesadas: {len(all_data)}")
    print(f"📊 Total de acordeones extraídos: {total_accordions}")
    print(f"💾 Datos guardados en: {output_file}")
    
    # Mostrar resumen por página
    print("\n📋 Resumen por página:")
    for page_key, page_data in sorted(all_data.items(), key=lambda x: x[1]['accordion_count'], reverse=True):
        print(f"   • {page_data['source_file']}: {page_data['accordion_count']} acordeones")


if __name__ == '__main__':
    main()
