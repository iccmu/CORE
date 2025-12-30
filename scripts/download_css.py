#!/usr/bin/env python3
"""Descargar CSS y recursos necesarios del sitio original"""

import os
import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSS_DIR = BASE_DIR / "madmusic_app" / "static" / "madmusic" / "css"
CSS_DIR.mkdir(parents=True, exist_ok=True)

# URLs de CSS a descargar
CSS_URLS = [
    "https://fonts.googleapis.com/css?family=Source+Sans+Pro:200,300,400,600,700,900,200italic,300italic,400italic,600italic,700italic,900italic",
    "https://fonts.googleapis.com/css?family=Slabo+27px",
    "https://madmusic.iccmu.es/wp-content/themes/iccmu/css/bootstrap.min.css",
    "https://madmusic.iccmu.es/wp-content/themes/iccmu/css/main.css?v=1.1",
    "https://madmusic.iccmu.es/wp-content/themes/iccmu/css/custom.css",
    "https://madmusic.iccmu.es/wp-content/themes/iccmu/css/font-awesome.min.css",
]

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
})

for url in CSS_URLS:
    try:
        print(f"Descargando {url}...")
        response = session.get(url, timeout=10)
        response.raise_for_status()
        
        # Nombre del archivo
        filename = url.split('/')[-1].split('?')[0] or 'style.css'
        if 'fonts.googleapis.com' in url:
            filename = url.split('family=')[1].split('&')[0].replace(':', '_') + '.css'
        
        filepath = CSS_DIR / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"  ✓ Guardado: {filename}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

print(f"\nCSS descargado en: {CSS_DIR}")





