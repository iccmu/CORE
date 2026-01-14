# Quickstart: Sistema de Exportación Estática

Guía rápida para empezar a usar el sistema de exportación estática.

## 🚀 Inicio Rápido (5 minutos)

### 1. Preparación

```bash
# Instalar dependencias (si no están instaladas)
pip install beautifulsoup4 lxml

# Recolectar archivos estáticos
python manage.py collectstatic --no-input
```

### 2. Primera Exportación

```bash
# Exportar el sitio madmusic a /tmp/export
python manage.py export_static_site \
  --site=madmusic.iccmu.es \
  --output=/tmp/export \
  --verbose
```

### 3. Ver el Resultado

```bash
# Abrir en navegador
open /tmp/export/index.html

# O en Linux
xdg-open /tmp/export/index.html
```

¡Listo! Ya tienes una versión offline navegable de tu sitio.

## 📦 Crear Backup Completo

```bash
# 1. Exportar y crear ZIP
python manage.py export_static_site \
  --site=madmusic.iccmu.es \
  --output=/tmp/export \
  --zip \
  --verbose

# El ZIP se crea en: /tmp/offline-backup-madmusic.iccmu.es-YYYYMMDD-HHMM.zip

# 2. Mover a directorio de backups
mkdir -p backups
mv /tmp/offline-backup-*.zip backups/
```

## ☁️ Backup a Azure

```bash
# 1. Configurar variables de entorno
export AZURE_ACCOUNT_NAME=mystorageaccount
export AZURE_ACCOUNT_KEY=your_key_here

# 2. Exportar y subir automáticamente
python manage.py export_static_site \
  --site=madmusic.iccmu.es \
  --output=/tmp/export \
  --zip \
  --upload-azure \
  --verbose
```

## 🔄 Casos de Uso Comunes

### Exportar Solo HTML (sin media)

Útil para preview rápido o testing:

```bash
python manage.py export_static_site \
  --site=madmusic.iccmu.es \
  --output=/tmp/export-html-only \
  --exclude-media \
  --verbose
```

### Exportar Múltiples Sites

```bash
# Script para exportar todos los sites
for site in madmusic.iccmu.es fondos.iccmu.es test.iccmu.es; do
  echo "Exportando $site..."
  python manage.py export_static_site \
    --site=$site \
    --output=/tmp/export-$site \
    --zip \
    --verbose
done
```

### Backup Programado (Linux/macOS)

```bash
# Editar crontab
crontab -e

# Agregar línea para backup diario a las 2 AM
0 2 * * * cd /path/to/project && /path/to/venv/bin/python manage.py export_static_site --site=madmusic.iccmu.es --output=/tmp/export --zip --upload-azure
```

## 🔐 Descargar Backups

### Opción 1: Descarga Staff (requiere login)

1. Inicia sesión como usuario staff
2. Visita: `https://madmusic.iccmu.es/download-offline-backup/`
3. El navegador descargará el backup más reciente

### Opción 2: Descarga con Token (no requiere login)

```bash
# 1. Generar token (requiere staff)
curl -X GET https://madmusic.iccmu.es/generate-download-token/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  | jq .

# Output:
# {
#   "token": "offline-backup-access:1234567890:abcdef...",
#   "download_url": "https://madmusic.iccmu.es/download-offline/?token=...",
#   "expires_in_seconds": 3600
# }

# 2. Usar la URL para descargar (válida 1 hora)
curl -O -J "https://madmusic.iccmu.es/download-offline/?token=..."
```

### Opción 3: Desde Azure

```bash
# 1. Obtener URL SAS (requiere staff)
curl -X GET https://madmusic.iccmu.es/download-from-azure/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  | jq .

# Output:
# {
#   "download_url": "https://mystorageaccount.blob.core.windows.net/...",
#   "expires_in_hours": 1
# }

# 2. Descargar desde Azure
curl -O -J "https://mystorageaccount.blob.core.windows.net/..."
```

## 📊 Listar Backups Disponibles

```bash
# Ver todos los backups (local + Azure)
curl -X GET https://madmusic.iccmu.es/list-backups/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  | jq .

# Output:
# {
#   "local": [
#     {
#       "name": "offline-backup-madmusic.iccmu.es-20260112-1430.zip",
#       "size_mb": 125.5,
#       "modified": 1736690400
#     }
#   ],
#   "azure": [
#     "offline-backup-madmusic.iccmu.es-20260112-1430.zip",
#     "offline-backup-madmusic.iccmu.es-20260111-1430.zip"
#   ]
# }
```

## 🧪 Testing

### Test Rápido

```bash
# Ejecutar todos los tests de export
pytest tests/cms/test_export.py -v
```

### Test con Coverage

```bash
# Ver coverage del módulo de export
pytest tests/cms/test_export.py --cov=cms.export --cov-report=term-missing
```

### Test Individual

```bash
# Solo un test específico
pytest tests/cms/test_export.py::StaticSiteExporterTestCase::test_export_creates_files -v
```

## 🐛 Debug

### Modo Verbose

Siempre usa `--verbose` para ver qué está haciendo el sistema:

```bash
python manage.py export_static_site \
  --site=madmusic.iccmu.es \
  --output=/tmp/export \
  --verbose
```

Output:

```
Exporting site: madmusic.iccmu.es (ID: 2)
Root page: <HomePage: Test Home>
Found 15 pages to export
Exporting: / (Test Home)
Exporting: /proyectos/ (Proyectos)
Exporting: /proyectos/madmusic/ (MadMusic)
...
Exported 15 pages (0 failed)
Copying static files from /path/to/staticfiles...
Static files copied to /tmp/export/static
Copying 243 media files...
Copied 243/243 media files
Export complete!
```

### Verificar Links Rotos

```bash
# Después de exportar, busca links absolutos que deberían ser relativos
grep -r 'href="/' /tmp/export/*.html | grep -v 'http' | head -20
```

### Verificar Media Files

```bash
# Listar media files copiados
find /tmp/export/media -type f | wc -l

# Ver tamaño total
du -sh /tmp/export/media
```

## 💡 Tips y Trucos

### 1. Reducir Tamaño del Export

```bash
# Excluir media para export rápido
python manage.py export_static_site \
  --site=madmusic.iccmu.es \
  --output=/tmp/export-small \
  --exclude-media

# Tamaño típico: ~5-10 MB (solo HTML + CSS + JS)
```

### 2. Export Incremental

```bash
# Script para mantener últimos 7 backups
#!/bin/bash
OUTPUT_DIR="/tmp/export-$(date +%Y%m%d)"

# Exportar
python manage.py export_static_site \
  --site=madmusic.iccmu.es \
  --output="$OUTPUT_DIR" \
  --zip

# Limpiar exports antiguos (mantener últimos 7)
cd /tmp
ls -t export-* | tail -n +8 | xargs rm -rf
```

### 3. Comparar Exports

```bash
# Útil para ver qué cambió entre exports
diff -r /tmp/export-old/ /tmp/export-new/ | head -50
```

### 4. Pre-visualizar Sin Servidor

```bash
# Python simple HTTP server
cd /tmp/export
python -m http.server 8000

# Visita: http://localhost:8000
```

### 5. Verificar Wagtail Sites

```bash
# Ver todos los sites disponibles
python manage.py shell
>>> from wagtail.models import Site
>>> for site in Site.objects.all():
...     print(f"ID: {site.id}, Hostname: {site.hostname}, Root: {site.root_page}")
```

## 📝 Integración con Homepage

Si quieres agregar un botón de descarga en tu homepage de Wagtail:

### 1. Template (cms/templates/cms/home_page.html)

```html
{% if request.user.is_staff %}
<div class="backup-download">
    <h3>🔐 Área Staff</h3>
    <p>Descarga una copia offline del sitio:</p>
    <a href="{% url 'download_offline_backup' %}" class="btn btn-primary">
        📦 Descargar Backup Offline
    </a>
    <a href="{% url 'generate_download_token' %}" class="btn btn-secondary">
        🔑 Generar Link de Descarga
    </a>
</div>
{% endif %}
```

### 2. JavaScript para Token

```javascript
// En tu template
<script>
async function generateDownloadLink() {
    const response = await fetch('/generate-download-token/');
    const data = await response.json();
    
    alert(`Link de descarga (válido 1 hora):\n${data.download_url}`);
    
    // O copiar al clipboard
    navigator.clipboard.writeText(data.download_url);
}
</script>

<button onclick="generateDownloadLink()">
    🔗 Generar Link Temporal
</button>
```

## 🚨 Troubleshooting Rápido

| Error | Solución |
|-------|----------|
| `STATIC_ROOT not found` | `python manage.py collectstatic --no-input` |
| `Site not found` | Verifica ID/hostname: `python manage.py shell` → `Site.objects.all()` |
| `Azure storage not available` | `pip install azure-storage-blob` |
| Links rotos | Verifica que URLs tengan trailing slash: `/page/` no `/page` |
| Imágenes no se ven | Revisa MEDIA_ROOT o configuración Azure |
| ZIP muy grande | Usa `--exclude-media` o optimiza imágenes |

## 📚 Más Información

- [README completo](STATIC_EXPORT_README.md) - Documentación detallada
- [Plan de implementación](.cursor/plans/static_site_export_system_7842b7a2.plan.md) - Arquitectura
- [Tests](tests/cms/test_export.py) - Ejemplos de uso

## 🎯 Próximos Pasos

1. ✅ Lee este quickstart
2. ✅ Ejecuta tu primera exportación
3. ✅ Configura backup automático (cron o GitHub Actions)
4. ✅ Configura Azure para storage a largo plazo
5. ✅ Agrega botón de descarga en homepage (opcional)

---

**¿Listo para empezar?** Ejecuta:

```bash
python manage.py export_static_site --site=madmusic.iccmu.es --output=/tmp/export --verbose
```
