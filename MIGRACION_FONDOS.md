# Plan de Migración: fondos_v1 → fondos_app

## 📍 Ubicación del Repositorio Original

**🔗 Repositorio GitHub:**
```
https://github.com/iccmu/fondos_v1
```

**✅ Repositorio local encontrado en:**
```
/Users/ivansimo/Documents/2025/FONDOS/
```

**Para clonar el repositorio (si necesitas la versión más actualizada):**
```bash
cd /Users/ivansimo/Documents/2025/
git clone https://github.com/iccmu/fondos_v1.git
```

**Estructura detectada:**
```
FONDOS/
├── manage.py
├── fondos/              # Proyecto Django
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── publicaciones/       # App principal
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── ...
├── templates/
├── static/
└── requirements.txt
```

## 🔍 Checklist de Análisis

### 1. Estructura del Proyecto
- [ ] Estructura de directorios
- [ ] Apps Django incluidas
- [ ] Archivos de configuración principales

### 2. Settings y Configuración
- [ ] `settings.py` - Configuración de base de datos
- [ ] `settings.py` - Configuración de Azure Blob Storage
- [ ] `settings.py` - ALLOWED_HOSTS y dominios
- [ ] `settings.py` - INSTALLED_APPS
- [ ] `settings.py` - MIDDLEWARE
- [ ] Variables de entorno utilizadas
- [ ] Configuración de static files y media files

### 3. Modelos de Base de Datos
- [ ] Lista de modelos y sus relaciones
- [ ] Nombres de tablas (app_label)
- [ ] Migraciones existentes
- [ ] Campos personalizados o especiales

### 4. URLs y Vistas
- [ ] Estructura de URLs (`urls.py`)
- [ ] Vistas principales (function-based y class-based)
- [ ] Patrones de URL utilizados
- [ ] Namespaces y app names

### 5. Templates
- [ ] Estructura de directorios de templates
- [ ] Template base utilizado
- [ ] Templates específicos por app
- [ ] Tags y filtros personalizados
- [ ] Inclusión de static files (CSS, JS, imágenes)

### 6. Static Files y Media
- [ ] Estructura de archivos estáticos
- [ ] CSS frameworks utilizados (Bootstrap, Tailwind, etc.)
- [ ] JavaScript libraries
- [ ] Imágenes y assets
- [ ] Configuración de Azure Blob Storage para media

### 7. Admin
- [ ] Configuraciones de admin.py por app
- [ ] ModelAdmin personalizados
- [ ] Actions personalizadas
- [ ] Filtros y búsquedas

### 8. Dependencias
- [ ] `requirements.txt` o `pyproject.toml`
- [ ] Versiones de Django y otras librerías
- [ ] Paquetes específicos de Azure

### 9. Funcionalidades Específicas
- [ ] Autenticación y permisos
- [ ] APIs o endpoints especiales
- [ ] Integraciones externas
- [ ] Tareas asíncronas (Celery, etc.)

### 10. Deployment
- [ ] Configuración de Azure App Service
- [ ] Variables de entorno en producción
- [ ] Configuración de WSGI/ASGI
- [ ] Logging y monitoreo

## 📝 Notas de Análisis

### Estructura Detectada
```
FONDOS/
├── manage.py
├── fondos/              # Proyecto Django
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   └── wsgi.py
├── publicaciones/       # App principal
│   ├── models.py        # Modelo: Edicion
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── templates/
├── templates/
│   ├── publicaciones/
│   └── admin/
├── static/
│   ├── css/
│   ├── images/
│   └── publicaciones/
└── requirements.txt
```

### Configuraciones Clave Documentadas

#### Base de Datos
- ✅ Tipo: PostgreSQL (psycopg2-binary)
- ⚠️ Configuración: Hardcodeada en settings.py (debe migrarse a variables de entorno)
- ✅ Host: `fondos-django-v1.postgres.database.azure.com`
- ✅ Database: `fondos-v1`
- ✅ User: `administrador`
- ⚠️ Password: Hardcodeada (mover a variable de entorno)
- ✅ Port: `5432`
- ✅ SSL: Requerido

#### Azure Blob Storage
- ⚠️ No detectado en settings.py inicial (revisar más abajo o en deployment.py)
- 📝 Revisar archivo `production.md` para más detalles

#### Dominios
- ✅ Dominio principal: `fondos-historicos-iccmu.azurewebsites.net`
- ✅ CSRF_TRUSTED_ORIGINS configurado
- ✅ ALLOWED_HOSTS: `['*']` (debe restringirse en producción)

#### Versiones
- ✅ Django: 4.2.4
- ✅ Python: 3.10 (según README)

### Modelos Identificados
| Modelo | App | Tabla | Campos Principales | Notas |
|--------|-----|-------|-------------------|-------|
| Edicion | publicaciones | publicaciones_edicion | 35 campos CharField | Modelo principal con signatura, autor, título, etc. |

**Campos del modelo Edicion:**
- signatura, autor_uniforme, autor_secundario_libretista, autor_secundario_arreglista_traductor
- titulo_propio, titulo_uniforme, idioma, incipit
- formato, numero_de_partes, contenido, descripcion_fisica, medidas
- completo, manuscrito_impreso, editor, lugar_publicacion, numero_de_plancha
- fecha_documento, fecha_atribuida, otras_signaturas_1, otras_signaturas_2
- materias, procedencia, colocado, codigo_de_barras
- encuadernacion, estado_de_conservacion, sellos_etiquetas_otras_marcas
- notas_de_ejemplar_1-4, observaciones, duplicados, observaciones_personales

### Templates Identificados
| Template | Ubicación | Propósito |
|----------|-----------|-----------|
| _base.html | templates/publicaciones/ | Template base |
| detail.html | templates/publicaciones/ | Vista detalle |
| search.html | templates/publicaciones/ | Búsqueda |
| home-view.html | templates/ | Vista principal |
| base.html | templates/admin/ | Admin personalizado |

### Dependencias Clave
```
Django==4.2.4
psycopg2-binary==2.9.7
whitenoise==6.5.0
python-dotenv==1.0.0
Unidecode==1.3.7
```

**Nota:** No se detecta `django-storages` en requirements.txt. Revisar si usa Azure Blob Storage o solo local/Whitenoise.

## 🎯 Plan de Migración

### Fase 1: Análisis (Actual)
- [x] Crear estructura base de fondos_app
- [ ] Analizar fondos_v1 completamente
- [ ] Documentar todas las configuraciones

### Fase 2: Preparación
- [ ] Crear modelos en fondos_app (respetando nombres de tablas)
- [ ] Configurar settings para reutilizar misma DB
- [ ] Preparar estructura de templates

### Fase 3: Migración Gradual
- [ ] Migrar modelos y migraciones
- [ ] Migrar vistas y URLs
- [ ] Migrar templates
- [ ] Migrar static files

### Fase 4: Pruebas y Validación
- [ ] Probar en entorno de desarrollo
- [ ] Verificar conexión a DB existente
- [ ] Validar funcionalidades principales

### Fase 5: Deployment
- [ ] Configurar variables de entorno
- [ ] Desplegar en Azure
- [ ] Verificar funcionamiento

## ⚠️ Consideraciones Importantes

1. **No romper fondos_v1**: El proyecto actual debe seguir funcionando hasta que la migración esté completa
2. **Reutilizar misma DB**: Usar `db_table` y `app_label` para mantener compatibilidad
3. **Mismo Blob Storage**: Reutilizar el mismo contenedor de Azure
4. **Migración gradual**: Migrar por partes, no todo de golpe
5. **Backup**: Hacer backup de la base de datos antes de cualquier cambio

