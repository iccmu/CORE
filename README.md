# ICCMU_PROYECTOS

## USANDO CONDA (core)

**Proyecto Django multidominio para las webs de proyectos del ICCMU**

Este repositorio será la nueva base común para las webs de proyectos del ICCMU (Fondos, Madmusic, etc.) en un solo despliegue Django.

## 📋 Contexto Importante

**⚠️ Ya existe un proyecto Django llamado `fondos_v1` desplegado en Azure con:**
- PostgreSQL
- Azure Blob Storage

**Este nuevo proyecto NO debe romper ni tocar ese despliegue.** La estrategia es:

1. Crear primero la infraestructura básica (`proyectos`, `fondos_app`, `madmusic`, `test_app`)
2. Más adelante, migrar el código existente de `fondos_v1` a `fondos_app`
3. Reutilizar la misma conexión PostgreSQL y Blob Storage cuando toque hacer el corte

## 🎯 Objetivos

- Crear un proyecto Django nuevo llamado `proyectos`
- Crear las apps:
  - `core` → modelos genéricos reutilizables
  - `fondos_app` → futura migración de la web actual de fondos
  - `madmusic` → web Madmusic
  - `test_app` → app mínima para pruebas / sanidad
- Preparar un sistema multi-dominio:
  - `fondos.iccmu.es` → rutas de `fondos_app`
  - `madmusic.iccmu.es` → rutas de `madmusic`
  - (otros dominios futuros → podrán añadirse igual)
- Configurar `settings.py` para leer:
  - PostgreSQL desde variables de entorno (las mismas que ya se usan en Azure si es posible)
  - Azure Blob Storage para MEDIA (también vía variables de entorno)
- De momento, dejar `fondos_app` con una estructura mínima, sin intentar replicar todavía todo el código de `fondos_v1`. La migración será una fase posterior.

## 📦 Requisitos Previos

- Python 3.10 o superior
- Django 4.2 o superior
- PostgreSQL (para producción, opcional en desarrollo)
- Variables de entorno configuradas (para producción)

### Dependencias Principales

```txt
Django>=4.2,<5.0
dj-database-url>=2.0.0
django-storages[azure]>=1.14.0
Pillow>=10.0.0
```

## 🏗️ Arquitectura de Proyecto

```
iccmu_proyectos/
├── manage.py
├── proyectos/                  # Proyecto Django
│   ├── __init__.py
│   ├── settings.py
│   ├── urls_root.py            # URLConf por defecto / fallback
│   ├── urls_fondos.py          # URLConf para fondos.iccmu.es
│   ├── urls_madmusic.py        # URLConf para madmusic.iccmu.es
│   ├── urls_test.py            # (opcional) URLConf para test_app u otros
│   ├── middleware.py           # DomainUrlConfMiddleware
│   └── wsgi.py
├── core/                       # Modelos genéricos (Proyecto, Entrada, Pagina, etc.)
├── fondos_app/                 # Futura migración del código de fondos_v1
├── madmusic/                   # Web Madmusic
├── test_app/                   # App de pruebas
└── templates/
```

## 🚀 Setup Local

### 1. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno (opcional para desarrollo)

Para desarrollo local, puedes usar SQLite (por defecto). Para conectar a PostgreSQL o Azure Blob Storage, crea un archivo `.env`:

```bash
# .env (no commiteado)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
AZURE_ACCOUNT_NAME=tu_cuenta
AZURE_ACCOUNT_KEY=tu_clave
AZURE_MEDIA_CONTAINER=media
```

### 4. Ejecutar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear superusuario (opcional)

```bash
python manage.py createsuperuser
```

### 6. Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

**Nota:** Para probar el multi-dominio localmente, puedes añadir entradas en `/etc/hosts`:

```
127.0.0.1 fondos.iccmu.es
127.0.0.1 madmusic.iccmu.es
```

## 🌐 Sistema Multi-dominio por Host

### Configuración en `proyectos/settings.py`

```python
ALLOWED_HOSTS = [
    "fondos.iccmu.es",
    "madmusic.iccmu.es",
    "localhost",  # para desarrollo
    "127.0.0.1",  # para desarrollo
    # se pueden añadir otros más adelante
]

ROOT_URLCONF = "proyectos.urls_root"

URLCONFS_BY_HOST = {
    "fondos.iccmu.es": "proyectos.urls_fondos",
    "madmusic.iccmu.es": "proyectos.urls_madmusic",
    # p.ej. "test.iccmu.es": "proyectos.urls_test"
}
```

### Middleware: `DomainUrlConfMiddleware`

**Archivo:** `proyectos/middleware.py`

```python
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class DomainUrlConfMiddleware:
    """
    Middleware que selecciona el URLConf apropiado basado en el dominio del host.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(":")[0]
        urlconf = settings.URLCONFS_BY_HOST.get(host, settings.ROOT_URLCONF)
        
        if urlconf != settings.ROOT_URLCONF:
            logger.debug(f"Usando URLConf '{urlconf}' para host '{host}'")
        
        request.urlconf = urlconf
        return self.get_response(request)
```

**En `settings.py`, añadir a `MIDDLEWARE`:**

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "proyectos.middleware.DomainUrlConfMiddleware",  # Añadir aquí
]
```

### URLConfs

**`proyectos/urls_root.py`:**

```python
from django.urls import path
from django.http import HttpResponse

def default_view(request):
    return HttpResponse("ICCMU – Proyecto multidominio (root)")

urlpatterns = [
    path("", default_view),
]
```

**`proyectos/urls_fondos.py`:**

```python
from django.urls import path, include

urlpatterns = [
    path("", include("fondos_app.urls")),
]
```

**`proyectos/urls_madmusic.py`:**

```python
from django.urls import path, include

urlpatterns = [
    path("", include("madmusic.urls")),
]
```

**`proyectos/urls_test.py` (opcional):**

```python
from django.urls import path, include

urlpatterns = [
    path("", include("test_app.urls")),
]
```

## 🧩 App Core: Modelos Genéricos

Estos modelos servirán para Madmusic y otros proyectos futuros. Más adelante también se pueden reutilizar para Fondos si encaja.

**`core/models.py`:**

```python
from django.db import models

class Proyecto(models.Model):
    slug = models.SlugField(unique=True)
    titulo = models.CharField(max_length=200)
    acronimo = models.CharField(max_length=50, blank=True)
    resumen = models.TextField(blank=True)
    cuerpo = models.TextField(blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    url_oficial = models.URLField(blank=True)

    def __str__(self):
        return self.titulo


class Entrada(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="entradas")
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    fecha_publicacion = models.DateField(auto_now_add=True)
    resumen = models.TextField(blank=True)
    cuerpo = models.TextField()
    imagen_destacada = models.ImageField(
        upload_to="entradas/portadas/%Y/%m/%d", blank=True, null=True
    )

    class Meta:
        ordering = ["-fecha_publicacion"]

    def __str__(self):
        return self.titulo


class Pagina(models.Model):
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.SET_NULL, null=True, blank=True, related_name="paginas"
    )
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    cuerpo = models.TextField()

    def __str__(self):
        return self.titulo
```

**Registrar estos modelos en `core/admin.py`:**

```python
from django.contrib import admin
from .models import Proyecto, Entrada, Pagina

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'slug', 'acronimo', 'fecha_inicio', 'fecha_fin']
    prepopulated_fields = {'slug': ('titulo',)}

@admin.register(Entrada)
class EntradaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'proyecto', 'fecha_publicacion']
    list_filter = ['proyecto', 'fecha_publicacion']
    prepopulated_fields = {'slug': ('titulo',)}

@admin.register(Pagina)
class PaginaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'slug', 'proyecto']
    prepopulated_fields = {'slug': ('titulo',)}
```

## 🧱 Apps Específicas

### fondos_app

Por ahora, solo necesitamos lo básico para comprobar que el dominio `fondos.iccmu.es` enruta bien:

**`fondos_app/urls.py`:**

```python
from django.urls import path
from .views import fondos_home

urlpatterns = [
    path("", fondos_home, name="fondos_home"),
]
```

**`fondos_app/views.py`:**

```python
from django.http import HttpResponse

def fondos_home(request):
    return HttpResponse("Futuros contenidos de FONDOS (fondos_app)")
```

Más adelante se migrará aquí todo lo que ahora está en el proyecto `fondos_v1` (modelos, vistas, templates…), tratando de reutilizar la misma base de datos y tablas.

### madmusic

**`madmusic/urls.py`:**

```python
from django.urls import path
from .views import madmusic_home

urlpatterns = [
    path("", madmusic_home, name="madmusic_home"),
]
```

**`madmusic/views.py`:**

```python
from django.shortcuts import render
from core.models import Proyecto

def madmusic_home(request):
    proyecto = Proyecto.objects.filter(slug="madmusic").first()
    return render(request, "madmusic/home.html", {"proyecto": proyecto})
```

**`templates/madmusic/home.html`** puede ser una plantilla mínima:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{% if proyecto %}{{ proyecto.titulo }}{% else %}Madmusic{% endif %}</title>
</head>
<body>
    <h1>{% if proyecto %}{{ proyecto.titulo }}{% else %}Madmusic{% endif %}</h1>
    {% if proyecto %}
        <p>{{ proyecto.resumen }}</p>
    {% endif %}
</body>
</html>
```

### test_app

App de pruebas para tener endpoints de diagnóstico si hace falta.

**`test_app/urls.py`:**

```python
from django.urls import path
from .views import test_home

urlpatterns = [
    path("", test_home, name="test_home"),
]
```

**`test_app/views.py`:**

```python
from django.http import JsonResponse

def test_home(request):
    return JsonResponse({
        "status": "ok",
        "message": "Test app funcionando correctamente",
        "host": request.get_host(),
    })
```

## 🗄️ Configuración de Base de Datos y Blob Storage

### ⚠️ Importante

La idea es reutilizar la conexión PostgreSQL y el Blob Storage que ya usa `fondos_v1`, pero eso se conectará más adelante, cuando el nuevo proyecto esté estable. De momento, el proyecto debe:

- Preparar `settings.py` para leer todo de variables de entorno
- Usar por defecto SQLite para desarrollo local si no hay variables definidas

### Configuración en `settings.py`

**Base de datos:**

```python
import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600),
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
```

**Azure Blob Storage:**

```python
AZURE_ACCOUNT_NAME = os.environ.get("AZURE_ACCOUNT_NAME")
AZURE_ACCOUNT_KEY = os.environ.get("AZURE_ACCOUNT_KEY")
AZURE_CONTAINER = os.environ.get("AZURE_MEDIA_CONTAINER", "media")

if AZURE_ACCOUNT_NAME and AZURE_ACCOUNT_KEY:
    INSTALLED_APPS += ["storages"]
    DEFAULT_FILE_STORAGE = "storages.backends.azure_storage.AzureStorage"
    AZURE_STORAGE_KEY = AZURE_ACCOUNT_KEY
    AZURE_STORAGE_ACCOUNT_NAME = AZURE_ACCOUNT_NAME
    AZURE_CONTAINER = AZURE_CONTAINER
    # La clase de storage personalizada se puede añadir más adelante
else:
    # Usar almacenamiento local en desarrollo
    MEDIA_ROOT = BASE_DIR / "media"
    MEDIA_URL = "/media/"
```

## ✅ Resumen de Tareas para Implementación

### Fase 1: Infraestructura Base

- [ ] Crear proyecto Django llamado `proyectos`
- [ ] Crear apps: `core`, `fondos_app`, `madmusic`, `test_app`
- [ ] Configurar `settings.py` con:
  - `ALLOWED_HOSTS`
  - `ROOT_URLCONF`
  - `URLCONFS_BY_HOST`
  - `DomainUrlConfMiddleware` añadido a `MIDDLEWARE`
  - Configuración de `DATABASES` basada en variable `DATABASE_URL` con fallback a SQLite
  - Bloque preparado para Azure Blob (sin necesidad de implementar todo ahora)

### Fase 2: URLConfs y Middleware

- [ ] Crear `proyectos/urls_root.py`
- [ ] Crear `proyectos/urls_fondos.py`
- [ ] Crear `proyectos/urls_madmusic.py`
- [ ] Crear `proyectos/urls_test.py` (opcional, básico)
- [ ] Implementar `DomainUrlConfMiddleware` en `proyectos/middleware.py`

### Fase 3: Modelos y Apps

- [ ] Implementar modelos `Proyecto`, `Entrada`, `Pagina` en `core/models.py`
- [ ] Registrar modelos en `core/admin.py`
- [ ] Crear `fondos_app/urls.py` y `fondos_app/views.py` con vista mínima
- [ ] Crear `madmusic/urls.py`, `madmusic/views.py` y plantilla mínima `templates/madmusic/home.html`
- [ ] Crear `test_app/urls.py` y `test_app/views.py` con vista mínima de prueba

### Fase 4: Migraciones y Testing

- [ ] Ejecutar `python manage.py makemigrations`
- [ ] Ejecutar `python manage.py migrate`
- [ ] Verificar que el multi-dominio funciona correctamente
- [ ] Probar cada dominio localmente (usando `/etc/hosts`)

### Fase 5: Migración de fondos_v1 (Futuro)

- [ ] Migrar código existente de `fondos_v1` dentro de `fondos_app`
- [ ] Respetar nombres de tablas / `app_label` para reutilizar la misma PostgreSQL
- [ ] Migrar templates y assets
- [ ] Realizar pruebas exhaustivas antes del corte

## 📝 Notas Adicionales

- El proyecto está diseñado para ser fácilmente extensible a nuevos dominios
- La migración de `fondos_v1` se realizará en una fase posterior, cuando la infraestructura base esté estable
- Se recomienda usar un entorno de staging antes de conectar a la base de datos de producción
- Considerar añadir tests automatizados para el middleware multi-dominio
