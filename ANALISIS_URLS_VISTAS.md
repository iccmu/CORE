# Análisis de URLs y Vistas - fondos_v1

## 📍 Ubicación del Repositorio

**Repositorio:** `/Users/ivansimo/Documents/2025/FONDOS/`  
**GitHub:** https://github.com/iccmu/fondos_v1

**⚠️ Protegido en .gitignore:** Sí (patrones añadidos para evitar commits accidentales)

---

## 🔗 Estructura de URLs

### URLs Principales (`fondos/urls.py`)

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view),                          # Vista home
    path('all/', include('publicaciones.urls')),  # Incluye URLs de publicaciones
    path('partituras/', partituras),              # Vista partituras
    path('arias/', arias),                        # Vista arias
    path('publicaciones/', views.post_search_view),      # Búsqueda
    path('publicaciones/<int:id>/', views.post_detail_view),  # Detalle
]
```

### URLs de la App (`publicaciones/urls.py`)

```python
urlpatterns = [
    path('', views.post_search_view, name='post_search'),      # Búsqueda
    path('<int:id>/', views.post_detail_view, name='post_detail'),  # Detalle
]
```

**Mapeo de URLs:**
- `/` → `home_view` (vista principal)
- `/all/` → `post_search_view` (búsqueda)
- `/all/<id>/` → `post_detail_view` (detalle)
- `/publicaciones/` → `post_search_view` (búsqueda - duplicado)
- `/publicaciones/<id>/` → `post_detail_view` (detalle - duplicado)
- `/partituras/` → `partituras` (vista específica)
- `/arias/` → `arias` (vista específica)

---

## 👁️ Vistas Principales

### 1. `post_search_view` (Búsqueda)

**Ubicación:** `publicaciones/views.py`

**Funcionalidad:**
- Búsqueda por query (`q`) en: `titulo_propio`, `titulo_uniforme`, `autor_uniforme`
- Filtro por procedencia (`f`) con dropdown
- Filtros por tipo: `manuscrito` y `musica_impresa` (checkboxes)
- Usa `unidecode` para búsqueda sin acentos
- Procesa el formato de cada objeto (Manuscritos/Impresos)

**Parámetros GET:**
- `q` - Query de búsqueda
- `f` - Filtro de procedencia
- `manuscrito` - Checkbox manuscritos
- `musica_impresa` - Checkbox música impresa

**Template:** `publicaciones/search.html`

**Context:**
```python
{
    "post_list": qs,              # QuerySet de Edicion
    "fondos_names": fondos_names, # Lista de fondos disponibles
    "query": query,               # Query de búsqueda
    "procedencia": procedencia_dropdown,
    "manuscrito": manuscrito_checkbox,
    "impreso": musica_impresa_checkbox,
}
```

### 2. `post_detail_view` (Detalle)

**Ubicación:** `publicaciones/views.py`

**Funcionalidad:**
- Muestra el detalle de una edición específica por ID
- Obtiene el objeto `Edicion` desde la base de datos

**Parámetros URL:**
- `<int:id>` - ID de la edición

**Template:** `publicaciones/detail.html`

**Context:**
```python
{
    "post": post_obj,  # Objeto Edicion
}
```

### 3. `home_view`

**Ubicación:** `fondos/views.py`

**Funcionalidad:**
- Vista principal de la aplicación
- Renderiza template `home-view.html`
- No pasa contexto (template estático o con datos del template)

**Template:** `home-view.html`

### 4. `partituras`

**Ubicación:** `fondos/views.py`

**Funcionalidad:**
- Vista para partituras/música electrónica
- Renderiza template `emusic.html`
- No pasa contexto

**Template:** `emusic.html`

### 5. `arias`

**Ubicación:** `fondos/views.py`

**Funcionalidad:**
- Vista para arias (Didone EU)
- Renderiza template `arias-didone-eu.html`
- No pasa contexto

**Template:** `arias-didone-eu.html`

---

## 🔍 Lógica de Búsqueda

### Proceso de Búsqueda:

1. **Query sin acentos:** Usa `unidecode` para normalizar la búsqueda
2. **Lookups:** Busca en 3 campos:
   - `titulo_propio__icontains`
   - `titulo_uniforme__icontains`
   - `autor_uniforme__icontains`

3. **Filtro de procedencia:**
   - Si es "Todos los fondos": filtra por lista de fondos
   - Si es específico: filtra por ese fondo exacto

4. **Procesamiento de formato:**
   - Itera sobre cada objeto para asignar formato
   - "Música manuscrita" → "Manuscritos"
   - "Música impresa" → "Impresos"

### Fondos Disponibles:
```python
fondos_names = [
    'Todos los fondos',
    'Fondo Convento de Santa Clara de Sevilla',
    'Fondo Vidal Llimona y Boceta'
]
```

---

## 📝 Notas para Migración

### URLs a Migrar:

1. **Búsqueda principal:**
   - `/all/` → `/fondos/` (en el nuevo proyecto)
   - Mantener funcionalidad de búsqueda y filtros

2. **Detalle:**
   - `/all/<id>/` → `/fondos/<id>/`
   - Mantener vista de detalle

3. **Vistas específicas:**
   - `/partituras/` y `/arias/` - Revisar si son necesarias

### Cambios Necesarios:

1. **Eliminar duplicados:** Hay URLs duplicadas (`/all/` y `/publicaciones/`)
2. **Normalizar rutas:** Usar prefijo `/fondos/` en el nuevo proyecto
3. **Mantener funcionalidad:** Búsqueda, filtros y detalle deben funcionar igual
4. **Template base:** Revisar `_base.html` para mantener diseño

### Dependencias:

- `unidecode` - Para búsqueda sin acentos (ya en requirements.txt)
- `Q` objects de Django - Para búsquedas complejas

---

## 🎯 Próximos Pasos

1. ✅ URLs analizadas
2. ✅ Vistas principales analizadas
3. ✅ `fondos/views.py` revisado (home_view, partituras, arias)
4. ⏭️ Revisar templates (`search.html`, `detail.html`, `_base.html`, `home-view.html`)
5. ⏭️ Revisar `publicaciones/admin.py`
6. ⏭️ Analizar static files y CSS
7. ⏭️ Revisar `fondos/choices.py` (fondos_choices)

