# Sistema de Exportación Estática para Wagtail

Sistema completo de exportación de sitios Wagtail a HTML estático standalone, permitiendo navegación offline sin servidor web.

## Índice

- [Características](#características)
- [Instalación](#instalación)
- [Uso Básico](#uso-básico)
- [Configuración](#configuración)
- [Descarga de Backups](#descarga-de-backups)
- [Automatización](#automatización)
- [Azure Integration](#azure-integration)
- [Tests](#tests)
- [Troubleshooting](#troubleshooting)

## Características

✅ **Exportación completa**: Todas las páginas publicadas de Wagtail  
✅ **URLs relativas**: Navegación offline sin servidor  
✅ **Assets incluidos**: Static files (CSS/JS) y media (imágenes/documentos)  
✅ **Múltiples sites**: Soporte para configuración multi-dominio  
✅ **Azure Blob Storage**: Upload automático de backups  
✅ **Descarga protegida**: Endpoints staff-only y con tokens firmados  
✅ **Testeable**: Suite completa de tests incluida  

## Instalación

### Dependencias

El sistema requiere las siguientes dependencias (ya incluidas en `requirements.txt`):

```bash
beautifulsoup4>=4.12.0
lxml>=4.9.0
```

Para Azure Blob Storage (opcional):

```bash
pip install azure-storage-blob
```

### Verificación

Verifica que el sistema está correctamente instalado:

```bash
python manage.py help export_static_site
```

## Uso Básico

### 1. Exportación Simple

Exporta un sitio a un directorio local:

```bash
python manage.py export_static_site --site=madmusic.iccmu.es --output=/tmp/export
```

### 2. Exportación con ZIP

Crea un archivo ZIP del sitio exportado:

```bash
python manage.py export_static_site --site=madmusic.iccmu.es --output=/tmp/export --zip
```

### 3. Exportación y Upload a Azure

Exporta, crea ZIP y sube a Azure Blob Storage:

```bash
python manage.py export_static_site --site=madmusic.iccmu.es --output=/tmp/export --zip --upload-azure
```

### 4. Exportación sin Media (más rápida)

Útil para testing o cuando solo se necesita el HTML:

```bash
python manage.py export_static_site --site=madmusic.iccmu.es --output=/tmp/export --exclude-media --verbose
```

## Argumentos del Comando

| Argumento | Requerido | Descripción | Ejemplo |
|-----------|-----------|-------------|---------|
| `--site` | ✅ | Site ID o hostname | `--site=1` o `--site=madmusic.iccmu.es` |
| `--output` | ❌ | Directorio de salida | `--output=/tmp/export` (default: `/tmp/export`) |
| `--zip` | ❌ | Crear archivo ZIP | `--zip` |
| `--upload-azure` | ❌ | Subir ZIP a Azure (requiere `--zip`) | `--upload-azure` |
| `--exclude-media` | ❌ | No copiar archivos media | `--exclude-media` |
| `--verbose` | ❌ | Salida detallada | `--verbose` |

## Configuración

### 1. Settings de Django

El sistema utiliza la configuración existente de Django/Wagtail:

```python
# settings.py

# Static files (requerido)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files - Local
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# O Media files - Azure Blob Storage
AZURE_ACCOUNT_NAME = os.environ.get("AZURE_ACCOUNT_NAME")
AZURE_ACCOUNT_KEY = os.environ.get("AZURE_ACCOUNT_KEY")
AZURE_CONTAINER = os.environ.get("AZURE_MEDIA_CONTAINER", "media")
```

### 2. Preparación: Collectstatic

**Importante**: Antes de exportar, ejecuta `collectstatic`:

```bash
python manage.py collectstatic --no-input
```

### 3. Directorio de Backups

Crea el directorio para almacenar backups locales:

```bash
mkdir -p backups
```

## Descarga de Backups

El sistema incluye varios endpoints para descargar backups:

### 1. Descarga Staff-Only

Requiere autenticación y permisos de staff:

```
GET /download-offline-backup/
```

**Uso desde navegador**: Simplemente visita la URL después de iniciar sesión como staff.

### 2. Descarga con Token Firmado

Genera un token de descarga temporal (válido 1 hora):

```bash
# 1. Genera el token (requiere staff)
curl -X GET https://madmusic.iccmu.es/generate-download-token/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID"

# Respuesta:
{
  "token": "...",
  "download_url": "https://madmusic.iccmu.es/download-offline/?token=...",
  "expires_in_seconds": 3600
}

# 2. Usa la URL de descarga (no requiere autenticación)
curl -O -J "https://madmusic.iccmu.es/download-offline/?token=..."
```

### 3. Descarga desde Azure

Genera una URL SAS temporal para descargar desde Azure:

```
GET /download-from-azure/
```

### 4. Listar Backups

Lista todos los backups disponibles (local y Azure):

```
GET /list-backups/
```

**Respuesta**:

```json
{
  "local": [
    {
      "name": "offline-backup-madmusic.iccmu.es-20260112-1430.zip",
      "size_mb": 125.5,
      "modified": 1736690400
    }
  ],
  "azure": [
    "offline-backup-madmusic.iccmu.es-20260112-1430.zip",
    "offline-backup-madmusic.iccmu.es-20260111-1430.zip"
  ]
}
```

## Automatización

### 1. Cron (Linux/macOS)

Ejecuta exportación diaria a las 2 AM:

```bash
crontab -e
```

Agrega:

```cron
# Exportación diaria del sitio madmusic
0 2 * * * cd /path/to/project && /path/to/venv/bin/python manage.py export_static_site --site=madmusic.iccmu.es --output=/tmp/export --zip --upload-azure >> /var/log/wagtail-export.log 2>&1

# Limpiar exports antiguos (mantener solo últimos 7 días)
0 3 * * * find /tmp/export-* -type d -mtime +7 -exec rm -rf {} \;
```

### 2. GitHub Actions

Crea `.github/workflows/static-backup.yml`:

```yaml
name: Export Static Backup

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  export:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run collectstatic
        run: |
          python manage.py collectstatic --no-input
      
      - name: Export and upload to Azure
        env:
          AZURE_ACCOUNT_NAME: ${{ secrets.AZURE_ACCOUNT_NAME }}
          AZURE_ACCOUNT_KEY: ${{ secrets.AZURE_ACCOUNT_KEY }}
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          python manage.py export_static_site \
            --site=madmusic.iccmu.es \
            --output=/tmp/export \
            --zip \
            --upload-azure \
            --verbose
      
      - name: Upload artifact (optional)
        uses: actions/upload-artifact@v3
        with:
          name: static-backup
          path: /tmp/offline-backup-*.zip
          retention-days: 7
```

### 3. Azure DevOps Pipeline

Crea `azure-pipelines.yml`:

```yaml
trigger: none

schedules:
- cron: "0 2 * * *"
  displayName: Daily backup at 2 AM
  branches:
    include:
    - main

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.11'
  
- script: |
    pip install -r requirements.txt
  displayName: 'Install dependencies'

- script: |
    python manage.py collectstatic --no-input
  displayName: 'Collect static files'

- script: |
    python manage.py export_static_site \
      --site=madmusic.iccmu.es \
      --output=$(Build.ArtifactStagingDirectory)/export \
      --zip \
      --upload-azure \
      --verbose
  displayName: 'Export and upload'
  env:
    AZURE_ACCOUNT_NAME: $(AZURE_ACCOUNT_NAME)
    AZURE_ACCOUNT_KEY: $(AZURE_ACCOUNT_KEY)
    DATABASE_URL: $(DATABASE_URL)
```

## Azure Integration

### 1. Configurar Storage Account

```bash
# Crear resource group (si no existe)
az group create --name myResourceGroup --location eastus

# Crear storage account
az storage account create \
  --name mystorageaccount \
  --resource-group myResourceGroup \
  --location eastus \
  --sku Standard_LRS

# Crear contenedor para backups
az storage container create \
  --name backups \
  --account-name mystorageaccount
```

### 2. Configurar Variables de Entorno

```bash
# .env o en tu servicio de hosting
AZURE_ACCOUNT_NAME=mystorageaccount
AZURE_ACCOUNT_KEY=your_account_key_here
```

### 3. Lifecycle Management (Opcional)

Configura políticas para eliminar backups antiguos automáticamente:

```json
{
  "rules": [
    {
      "enabled": true,
      "name": "delete-old-backups",
      "type": "Lifecycle",
      "definition": {
        "filters": {
          "blobTypes": ["blockBlob"],
          "prefixMatch": ["backups/offline-backup-"]
        },
        "actions": {
          "baseBlob": {
            "delete": {
              "daysAfterModificationGreaterThan": 90
            },
            "tierToCool": {
              "daysAfterModificationGreaterThan": 30
            }
          }
        }
      }
    }
  ]
}
```

### 4. Limpiar Backups Antiguos

El sistema incluye un método para limpiar backups antiguos:

```python
from cms.export.azure_uploader import AzureBackupUploader

uploader = AzureBackupUploader()
uploader.delete_old_backups(keep_count=10)  # Mantiene solo los últimos 10
```

## Tests

### Ejecutar Tests

```bash
# Todos los tests de export
pytest tests/cms/test_export.py -v

# Solo tests de exporter
pytest tests/cms/test_export.py::StaticSiteExporterTestCase -v

# Solo tests de rewriter
pytest tests/cms/test_export.py::HTMLRewriterTestCase -v

# Solo tests de vistas
pytest tests/cms/test_export.py::DownloadViewsTestCase -v
```

### Coverage

```bash
pytest tests/cms/test_export.py --cov=cms.export --cov-report=html
```

## Estructura del Export

El sitio exportado tiene la siguiente estructura:

```
export/
├── index.html                 # Página raíz
├── proyectos/
│   └── madmusic/
│       └── index.html
├── noticias/
│   ├── index.html
│   └── evento-2025/
│       └── index.html
├── static/                    # Static files (CSS, JS)
│   ├── admin/
│   ├── madmusic/
│   └── wagtailadmin/
└── media/                     # Media files (imágenes, docs)
    ├── images/
    └── documents/
```

### Características del HTML Exportado

- **URLs relativas**: Todos los links internos usan rutas relativas
- **Navegación offline**: Funciona con `file://` protocol
- **Notice offline**: Banner amarillo indicando versión offline
- **Sin canonical links**: Removidos para evitar confusión
- **Wagtail documents**: Convertidos a paths directos de media

## Troubleshooting

### Error: STATIC_ROOT not found

**Problema**: No se han recolectado los archivos estáticos.

**Solución**:

```bash
python manage.py collectstatic --no-input
```

### Error: Site not found

**Problema**: El site ID o hostname no existe.

**Solución**: Lista los sites disponibles:

```python
from wagtail.models import Site
for site in Site.objects.all():
    print(f"ID: {site.id}, Hostname: {site.hostname}")
```

### Error: Azure storage not available

**Problema**: Falta el paquete `azure-storage-blob`.

**Solución**:

```bash
pip install azure-storage-blob
```

### Links internos rotos

**Problema**: Los links no funcionan en el export.

**Debugging**:

1. Verifica que las páginas tengan trailing slashes: `/page/` no `/page`
2. Revisa el HTML exportado con `--verbose`
3. Comprueba que `page.url` retorna la URL correcta

### Imágenes no se muestran

**Problema**: Las imágenes no aparecen en el export offline.

**Debugging**:

1. Verifica que las imágenes estén en MEDIA_ROOT (local) o Azure
2. Usa `--verbose` para ver qué media files se están copiando
3. Comprueba que las rutas relativas sean correctas en el HTML

### ZIP muy grande

**Problema**: El ZIP supera los 500 MB.

**Soluciones**:

- Usa `--exclude-media` para testing
- Optimiza imágenes antes de subir a Wagtail
- Implementa compresión de imágenes en el pipeline

## Arquitectura

```
┌─────────────────────────────────────────────────┐
│  Management Command: export_static_site         │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  StaticSiteExporter                             │
│  - Obtiene páginas de Wagtail                   │
│  - Renderiza con Django Test Client             │
│  - Coordina reescritura y copia de assets       │
└────────────────┬────────────────────────────────┘
                 │
      ┌──────────┼──────────┐
      │          │          │
      ▼          ▼          ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│ HTML    │ │ Static  │ │ Media   │
│Rewriter │ │ Copy    │ │ Copy    │
└─────────┘ └─────────┘ └─────────┘
      │          │          │
      └──────────┼──────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  ZIP Creation                                   │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Azure Blob Storage (opcional)                  │
└─────────────────────────────────────────────────┘
```

## Pitfalls y Soluciones Implementadas

✅ **Trailing slashes**: Normalizados automáticamente  
✅ **Query strings**: Ignoradas en export  
✅ **Canonical links**: Removidos automáticamente  
✅ **JavaScript dinámico**: Notice de funcionalidad online-only  
✅ **Wagtail documents**: Convertidos a media paths directos  
✅ **Imágenes renditions**: Copiadas automáticamente  
✅ **Multi-site navigation**: Soporte para export por site  
✅ **Azure Blob Storage**: Download automático de media  

## Contribuir

Para agregar nuevas funcionalidades:

1. Agrega tests en `tests/cms/test_export.py`
2. Implementa la funcionalidad
3. Actualiza esta documentación
4. Ejecuta los tests: `pytest tests/cms/test_export.py -v`

## Soporte

Para preguntas o issues:

- Revisa esta documentación
- Revisa los tests para ejemplos de uso
- Ejecuta con `--verbose` para debugging

## Licencia

Este sistema es parte del proyecto ICCMU CORE.
