#!/usr/bin/env python3
"""
Web Scraper recursivo para https://madmusic.iccmu.es/
Extrae todo el contenido incluyendo imágenes y maneja menús desplegables.
"""

import os
import re
import sys
import time
import urllib.parse
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


class MadMusicScraper:
    def __init__(self, base_url="https://madmusic.iccmu.es/", output_dir="scraped_content"):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.output_dir = Path(output_dir)
        self.visited_urls = set()
        self.failed_urls = set()
        self.downloaded_images = set()
        
        # Crear directorios
        self.html_dir = self.output_dir / "html"
        self.images_dir = self.output_dir / "images"
        self.html_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar sesión de requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def is_valid_url(self, url):
        """Verificar si la URL es válida para scraping"""
        parsed = urlparse(url)
        
        # Solo URLs del mismo dominio
        if parsed.netloc != self.domain:
            return False
        
        # Excluir archivos comunes que no queremos
        excluded_extensions = {'.pdf', '.zip', '.doc', '.docx', '.xls', '.xlsx'}
        if any(url.lower().endswith(ext) for ext in excluded_extensions):
            return False
        
        # Excluir URLs de administración y API
        excluded_paths = ['/admin/', '/api/', '/wp-admin/', '/wp-json/']
        if any(path in url for path in excluded_paths):
            return False
        
        return True
    
    def normalize_url(self, url):
        """Normalizar URL eliminando fragmentos y parámetros de tracking"""
        parsed = urlparse(url)
        # Eliminar fragmentos (#) y algunos parámetros comunes de tracking
        clean_params = {k: v for k, v in urllib.parse.parse_qs(parsed.query).items() 
                       if k not in ['utm_source', 'utm_medium', 'utm_campaign', 'fbclid']}
        clean_query = urllib.parse.urlencode(clean_params, doseq=True)
        
        normalized = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            clean_query,
            ''  # Sin fragmento
        ))
        
        return normalized.rstrip('/')
    
    def extract_links(self, soup, current_url):
        """Extraer todos los enlaces de una página"""
        links = set()
        
        # Enlaces de <a>
        for tag in soup.find_all('a', href=True):
            href = tag['href']
            absolute_url = urljoin(current_url, href)
            normalized = self.normalize_url(absolute_url)
            if self.is_valid_url(normalized):
                links.add(normalized)
        
        return links
    
    def extract_images(self, soup, current_url):
        """Extraer todas las imágenes de una página"""
        images = []
        
        # Imágenes en <img>
        for img in soup.find_all('img', src=True):
            src = img['src']
            absolute_url = urljoin(current_url, src)
            if urlparse(absolute_url).netloc == self.domain or not urlparse(absolute_url).netloc:
                images.append(absolute_url)
        
        # Imágenes en CSS background-image
        for tag in soup.find_all(style=True):
            style = tag.get('style', '')
            bg_match = re.search(r'background-image:\s*url\(["\']?([^"\']+)["\']?\)', style)
            if bg_match:
                img_url = bg_match.group(1)
                absolute_url = urljoin(current_url, img_url)
                if urlparse(absolute_url).netloc == self.domain or not urlparse(absolute_url).netloc:
                    images.append(absolute_url)
        
        # Imágenes en <source> (para responsive images)
        for source in soup.find_all('source', srcset=True):
            srcset = source['srcset']
            for src in srcset.split(','):
                img_url = src.strip().split()[0]
                absolute_url = urljoin(current_url, img_url)
                if urlparse(absolute_url).netloc == self.domain or not urlparse(absolute_url).netloc:
                    images.append(absolute_url)
        
        return list(set(images))  # Eliminar duplicados
    
    def download_image(self, img_url):
        """Descargar una imagen"""
        if img_url in self.downloaded_images:
            return
        
        try:
            response = self.session.get(img_url, timeout=10, stream=True)
            response.raise_for_status()
            
            # Determinar extensión
            parsed = urlparse(img_url)
            ext = Path(parsed.path).suffix or '.jpg'
            if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']:
                ext = '.jpg'
            
            # Crear nombre de archivo seguro
            safe_name = re.sub(r'[^\w\-_\.]', '_', Path(parsed.path).name)
            if not safe_name.endswith(ext):
                safe_name += ext
            
            # Guardar imagen
            img_path = self.images_dir / safe_name
            counter = 1
            while img_path.exists():
                name_part = img_path.stem
                img_path = self.images_dir / f"{name_part}_{counter}{ext}"
                counter += 1
            
            with open(img_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.downloaded_images.add(img_url)
            print(f"      [IMG] {safe_name}", flush=True)
            
        except Exception as e:
            print(f"      [!] Error imagen: {str(e)[:50]}", flush=True)
    
    def url_to_filename(self, url):
        """Convertir URL a nombre de archivo seguro"""
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        
        if not path:
            return "index.html"
        
        # Reemplazar caracteres especiales
        safe_name = re.sub(r'[^\w\-_/]', '_', path)
        
        # Asegurar que termine en .html
        if not safe_name.endswith('.html'):
            if safe_name.endswith('/'):
                safe_name = safe_name.rstrip('/') + '/index.html'
            else:
                safe_name += '.html'
        
        return safe_name
    
    def scrape_page(self, url):
        """Scrapear una página individual"""
        if url in self.visited_urls:
            return set()
        
        page_num = len(self.visited_urls) + 1
        print(f"\n[{page_num}] {url}", flush=True)
        self.visited_urls.add(url)
        
        try:
            # Descargar página
            print(f"  [→] Descargando...", end='', flush=True)
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            print(f" ✓ ({len(response.content)} bytes)", flush=True)
            
            # Parsear HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Guardar HTML
            safe_filename = self.url_to_filename(url)
            html_path = self.html_dir / safe_filename
            html_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            print(f"  [HTML] Guardado: {safe_filename}", flush=True)
            
            # Extraer y descargar imágenes
            images = self.extract_images(soup, url)
            if images:
                print(f"  [→] Descargando {len(images)} imágenes...", flush=True)
                for img_url in images:
                    self.download_image(img_url)
            
            # Extraer enlaces
            links = self.extract_links(soup, url)
            print(f"  [→] Encontrados {len(links)} enlaces", flush=True)
            
            return links
            
        except requests.exceptions.Timeout:
            print(f"  [!] TIMEOUT", flush=True)
            self.failed_urls.add(url)
            return set()
        except requests.exceptions.RequestException as e:
            print(f"  [!] Error HTTP: {str(e)[:60]}", flush=True)
            self.failed_urls.add(url)
            return set()
        except Exception as e:
            print(f"  [!] Error: {str(e)[:60]}", flush=True)
            self.failed_urls.add(url)
            return set()
    
    def scrape_recursive(self, start_url=None, max_depth=10, current_depth=0):
        """Scrapear recursivamente desde una URL inicial"""
        if start_url is None:
            start_url = self.base_url
        
        if current_depth >= max_depth:
            return
        
        normalized_start = self.normalize_url(start_url)
        if not self.is_valid_url(normalized_start):
            return
        
        # Scrapear página actual
        links = self.scrape_page(normalized_start)
        
        # Mostrar progreso
        print(f"\n  [📊] Progreso: {len(self.visited_urls)} páginas | {len(self.downloaded_images)} imágenes | {len(self.failed_urls)} errores", flush=True)
        
        # Scrapear enlaces encontrados recursivamente
        new_links = [link for link in links if link not in self.visited_urls]
        if new_links:
            print(f"  [→] Profundidad {current_depth + 1}/{max_depth}: {len(new_links)} enlaces nuevos\n", flush=True)
        
        for link in new_links:
            time.sleep(0.5)  # Pausa entre requests
            self.scrape_recursive(link, max_depth, current_depth + 1)
    
    def generate_report(self):
        """Generar reporte del scraping"""
        report_path = self.output_dir / "scraping_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("REPORTE DE WEB SCRAPING - madmusic.iccmu.es\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"URL Base: {self.base_url}\n")
            f.write(f"Total páginas scrapeadas: {len(self.visited_urls)}\n")
            f.write(f"Total imágenes descargadas: {len(self.downloaded_images)}\n")
            f.write(f"URLs fallidas: {len(self.failed_urls)}\n\n")
            
            f.write("PÁGINAS SCRAPEADAS:\n")
            f.write("-" * 80 + "\n")
            for url in sorted(self.visited_urls):
                f.write(f"  {url}\n")
            
            if self.failed_urls:
                f.write("\nURLs FALLIDAS:\n")
                f.write("-" * 80 + "\n")
                for url in sorted(self.failed_urls):
                    f.write(f"  {url}\n")
        
        print(f"\n[Reporte] Generado en: {report_path}", flush=True)


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Web Scraper para madmusic.iccmu.es')
    parser.add_argument('--url', default='https://madmusic.iccmu.es/',
                       help='URL inicial para scraping')
    parser.add_argument('--output', default='scraped_madmusic',
                       help='Directorio de salida')
    parser.add_argument('--depth', type=int, default=5,
                       help='Profundidad máxima de recursión')
    
    args = parser.parse_args()
    
    scraper = MadMusicScraper(base_url=args.url, output_dir=args.output)
    
    try:
        print("=" * 80, flush=True)
        print("WEB SCRAPING - madmusic.iccmu.es", flush=True)
        print("=" * 80, flush=True)
        print(f"URL Base: {args.url}", flush=True)
        print(f"Directorio: {args.output}", flush=True)
        print(f"Profundidad: {args.depth}", flush=True)
        print("=" * 80, flush=True)
        print("", flush=True)
        
        scraper.scrape_recursive(max_depth=args.depth)
        
        print("\n" + "=" * 80, flush=True)
        print("SCRAPING COMPLETADO", flush=True)
        print("=" * 80, flush=True)
        print(f"Páginas: {len(scraper.visited_urls)}", flush=True)
        print(f"Imágenes: {len(scraper.downloaded_images)}", flush=True)
        print(f"Errores: {len(scraper.failed_urls)}", flush=True)
        
        scraper.generate_report()
        
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario", flush=True)
        scraper.generate_report()
    except Exception as e:
        print(f"\n\n[!] Error fatal: {e}", flush=True)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()





