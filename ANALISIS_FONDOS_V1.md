# Análisis Rápido: fondos_v1 → fondos_app

## 📋 Resumen Ejecutivo

**🔗 Repositorio GitHub:** https://github.com/iccmu/fondos_v1

**Ubicación local:** `/Users/ivansimo/Documents/2025/FONDOS/`

**Estado:** ✅ Proyecto Django 4.2.4 funcionando en producción (Azure)

---

## 🏗️ Estructura del Proyecto

```
FONDOS/
├── fondos/              # Proyecto Django principal
│   ├── settings.py      # ⚠️ Credenciales hardcodeadas
│   ├── urls.py
│   ├── views.py
│   └── wsgi.py
├── publicaciones/        # App principal con modelo Edicion
│   ├── models.py        # Modelo: Edicion (35 campos)
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── templates/
├── templates/
│   ├── publicaciones/   # Templates de la app
│   └── admin/           # Admin personalizado
└── static/
    ├── css/             # Estilos CSS personalizados
    ├── images/          # Imágenes y logos
    └── publicaciones/
```

---

## 🗄️ Base de Datos

**Tipo:** PostgreSQL (Azure)

**Configuración actual (settings.py):**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'fondos-v1',
        'USER': 'administrador',
        'PASSWORD': 'Gaztambide_1',  # ⚠️ Hardcodeado
        'HOST': 'fondos-django-v1.postgres.database.azure.com',
        'PORT': '5432',
        'OPTIONS': {'sslmode': 'require'}
    }
}
```

**⚠️ Acción requerida:** Migrar a variables de entorno usando `dj-database-url`

---

## 📦 Modelo Principal: Edicion

**App:** `publicaciones`  
**Tabla:** `publicaciones_edicion` (automático)

**Campos (35 total):**
- Identificación: `signatura`, `codigo_de_barras`, `otras_signaturas_1`, `otras_signaturas_2`
- Autores: `autor_uniforme`, `autor_secundario_libretista`, `autor_secundario_arreglista_traductor`
- Títulos: `titulo_propio`, `titulo_uniforme`
- Fechas: `fecha_documento`, `fecha_atribuida`
- Físico: `formato`, `numero_de_partes`, `descripcion_fisica`, `medidas`, `completo`
- Tipo: `manuscrito_impreso`
- Editorial: `editor`, `lugar_publicacion`, `numero_de_plancha`
- Contenido: `idioma`, `incipit`, `contenido`
- Clasificación: `materias`, `procedencia`, `colocado`
- Conservación: `encuadernacion`, `estado_de_conservacion`, `sellos_etiquetas_otras_marcas`
- Notas: `notas_de_ejemplar_1-4`, `observaciones`, `observaciones_personales`, `duplicados`

**Propiedad personalizada:**
- `get_formato`: Retorna 'Manuscritos' o 'Impresos' según `manuscrito_impreso`

---

## 🎨 Templates y Static Files

### Templates principales:
- `templates/publicaciones/_base.html` - Template base
- `templates/publicaciones/detail.html` - Vista detalle
- `templates/publicaciones/search.html` - Búsqueda
- `templates/home-view.html` - Vista principal
- `templates/admin/base.html` - Admin personalizado

### CSS personalizado:
- `static/css/_post_list.css` - Estilos para listado
- `static/publicaciones/_base.css` - Estilos base

### Imágenes:
- Logos ICCMU, Carlos III, Complutense, ERC
- Imágenes de fondos documentales
- Favicon

**Static Files:** Usa Whitenoise (no Azure Blob Storage para static)

**Media Files:** ⚠️ Comentado en settings.py (revisar si se usa en producción)

---

## 🔗 URLs y Vistas

**Revisar:**
- `fondos/urls.py` - URLs principales
- `publicaciones/urls.py` - URLs de la app
- `publicaciones/views.py` - Vistas principales

---

## 📦 Dependencias

```txt
Django==4.2.4
psycopg2-binary==2.9.7
whitenoise==6.5.0
python-dotenv==1.0.0
Unidecode==1.3.7
```

**Nota:** No usa `django-storages` → Probablemente no usa Azure Blob Storage para media

---

## ⚠️ Puntos Críticos para Migración

1. **Credenciales hardcodeadas** → Migrar a variables de entorno
2. **Nombre de tabla** → Mantener `publicaciones_edicion` usando `db_table` en Meta
3. **App label** → Mantener `publicaciones` usando `app_label` en Meta
4. **Static files** → Copiar estructura de `static/` a `fondos_app/static/`
5. **Templates** → Migrar a `fondos_app/templates/`
6. **Admin personalizado** → Revisar `publicaciones/admin.py`

---

## 📝 Próximos Pasos

1. ✅ Análisis inicial completado
2. ⏭️ Revisar URLs y vistas en detalle
3. ⏭️ Revisar admin.py y configuraciones
4. ⏭️ Crear modelos en fondos_app respetando nombres de tablas
5. ⏭️ Migrar templates y static files
6. ⏭️ Configurar settings para reutilizar misma DB

---

## 🔍 Archivos Clave a Revisar

- [ ] `fondos/urls.py` - Estructura de URLs
- [ ] `publicaciones/views.py` - Lógica de negocio
- [ ] `publicaciones/admin.py` - Configuración admin
- [ ] `publicaciones/urls.py` - URLs de la app
- [ ] `templates/publicaciones/*.html` - Todos los templates
- [ ] `static/css/*.css` - Estilos CSS
- [ ] `fondos/deployment.py` - Si existe, configuraciones de deployment

