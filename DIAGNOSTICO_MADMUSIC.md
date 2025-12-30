# Diagnóstico - Sitio Madmusic

## Problemas Comunes y Soluciones

### 1. Archivos estáticos no se cargan

**Síntoma:** CSS e imágenes no aparecen

**Solución:**
```bash
# Ejecutar collectstatic
python manage.py collectstatic

# Verificar que los archivos estén en:
ls staticfiles/madmusic/
```

### 2. Rutas de imágenes incorrectas

**Verificar:**
- Las imágenes deben estar en: `madmusic_app/static/madmusic/images/`
- Los nombres de archivo deben coincidir exactamente (case-sensitive)

### 3. CSS no se aplica

**Verificar:**
- Los CSS deben estar en: `madmusic_app/static/madmusic/css/`
- Verificar que `main.css` y `custom.css` se carguen correctamente

### 4. Menú no funciona

**Verificar:**
- jQuery debe cargarse antes que Bootstrap
- El JavaScript `main.js` debe estar presente

### 5. Rutas de páginas no funcionan

**Verificar:**
- Las páginas deben crearse en el admin con los slugs correctos
- Ejemplo: slug "proyecto-madmusic" para la página principal del proyecto

## Checklist de Verificación

- [ ] Archivos estáticos copiados (`collectstatic` ejecutado)
- [ ] Imágenes en `madmusic_app/static/madmusic/images/`
- [ ] CSS en `madmusic_app/static/madmusic/css/`
- [ ] JavaScript en `madmusic_app/static/madmusic/js/`
- [ ] Template base existe: `templates/madmusic/base.html`
- [ ] Vistas configuradas en `madmusic_app/views.py`
- [ ] URLs configuradas en `madmusic_app/urls.py`
- [ ] Proyecto creado en admin con slug "madmusic"
- [ ] Páginas creadas en admin con slugs correspondientes

## Comandos Útiles

```bash
# Verificar estructura de archivos estáticos
find madmusic_app/static -type f | head -20

# Verificar que las imágenes existan
ls madmusic_app/static/madmusic/images/ | grep -i "Danza\|banner"

# Verificar configuración Django
python manage.py check

# Probar servidor
python manage.py runserver
```

## URLs para Probar

- `http://127.0.0.1:8000/madmusic/` - Página principal
- `http://127.0.0.1:8000/madmusic/noticias/` - Listado de noticias
- `http://127.0.0.1:8000/madmusic/proyecto-madmusic/` - Página del proyecto
- `http://127.0.0.1:8000/static/madmusic/css/main.css` - Verificar CSS
- `http://127.0.0.1:8000/static/madmusic/images/Danza_Goya.jpg` - Verificar imagen





