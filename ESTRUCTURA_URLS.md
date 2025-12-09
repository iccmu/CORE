# Estructura de URLs - Multi-dominio

## 🎯 Objetivo

Configurar las URLs para que funcionen tanto en desarrollo local como en producción con dominios específicos.

## 📍 Configuración Actual

### Desarrollo Local (localhost)

**URLs disponibles:**
- `http://127.0.0.1:8000/` → Índice principal
- `http://127.0.0.1:8000/fondos/` → App Fondos
- `http://127.0.0.1:8000/madmusic/` → App Madmusic
- `http://127.0.0.1:8000/test/` → App Test

**Archivo:** `proyectos/urls_root.py`
```python
urlpatterns = [
    path("", index_view, name="index"),
    path("fondos/", include("fondos_app.urls")),
    path("madmusic/", include("madmusic_app.urls")),
    path("test/", include("test_app.urls")),
]
```

### Producción (Dominios específicos)

**URLs disponibles:**
- `https://fondos.iccmu.es/` → App Fondos (sin prefijo)
- `https://madmusic.iccmu.es/` → App Madmusic (sin prefijo)
- `https://test.iccmu.es/` → App Test (sin prefijo)

**Archivos:**
- `proyectos/urls_fondos.py` → Para `fondos.iccmu.es`
- `proyectos/urls_madmusic.py` → Para `madmusic.iccmu.es`
- `proyectos/urls_test.py` → Para `test.iccmu.es`

**Ejemplo `urls_fondos.py`:**
```python
urlpatterns = [
    path("", include("fondos_app.urls")),  # Sin prefijo
]
```

## 🔄 Cómo Funciona

### Middleware Multi-dominio

El `DomainUrlConfMiddleware` detecta el dominio y selecciona el URLConf apropiado:

1. **Si el dominio es `fondos.iccmu.es`:**
   - Usa `proyectos.urls_fondos`
   - Las rutas de `fondos_app.urls` se sirven desde `/` (raíz)

2. **Si el dominio es `madmusic.iccmu.es`:**
   - Usa `proyectos.urls_madmusic`
   - Las rutas de `madmusic_app.urls` se sirven desde `/` (raíz)

3. **Si el dominio es `test.iccmu.es`:**
   - Usa `proyectos.urls_test`
   - Las rutas de `test_app.urls` se sirven desde `/` (raíz)

4. **Si el dominio es `localhost` o `127.0.0.1`:**
   - Usa `proyectos.urls_root`
   - Las rutas tienen prefijos: `/fondos/`, `/madmusic/`, `/test/`, etc.

### Configuración en settings.py

```python
ROOT_URLCONF = 'proyectos.urls_root'

URLCONFS_BY_HOST = {
    "fondos.iccmu.es": "proyectos.urls_fondos",
    "madmusic.iccmu.es": "proyectos.urls_madmusic",
    "test.iccmu.es": "proyectos.urls_test",
}
```

## 📝 Estructura de URLs por App

### fondos_app/urls.py

**Estructura actual (básica):**
```python
urlpatterns = [
    path("", fondos_home, name="fondos_home"),
]
```

**Estructura futura (después de migración):**
```python
urlpatterns = [
    path("", post_search_view, name="fondos_search"),      # Búsqueda principal
    path("<int:id>/", post_detail_view, name="fondos_detail"),  # Detalle
    # Otras rutas que vengan de fondos_v1
]
```

**Comportamiento:**
- En local: `http://127.0.0.1:8000/fondos/` → `fondos_home`
- En producción: `https://fondos.iccmu.es/` → `fondos_home`

### madmusic_app/urls.py

**Estructura actual:**
```python
urlpatterns = [
    path("", madmusic_home, name="madmusic_home"),
]
```

**Comportamiento:**
- En local: `http://127.0.0.1:8000/madmusic/` → `madmusic_home`
- En producción: `https://madmusic.iccmu.es/` → `madmusic_home`

### test_app/urls.py

**Estructura actual:**
```python
urlpatterns = [
    path("", test_home, name="test_home"),
    path("api/", test_api, name="test_api"),  # Endpoint JSON
]
```

**Comportamiento:**
- En local: `http://127.0.0.1:8000/test/` → `test_home`
- En producción: `https://test.iccmu.es/` → `test_home`
- Endpoint JSON: `https://test.iccmu.es/api/` → `test_api`

## ✅ Verificación

Para verificar que funciona correctamente:

1. **En desarrollo local:**
   ```bash
   python manage.py runserver
   # Acceder a http://127.0.0.1:8000/fondos/
   ```

2. **Simular dominio en local (opcional):**
   ```bash
   # Añadir a /etc/hosts:
   127.0.0.1 fondos.iccmu.es
   127.0.0.1 madmusic.iccmu.es
   127.0.0.1 test.iccmu.es
   
   # Acceder a:
   # http://fondos.iccmu.es:8000/
   # http://madmusic.iccmu.es:8000/
   # http://test.iccmu.es:8000/
   ```

## 🔧 Migración de URLs desde fondos_v1

Cuando migremos las URLs de `fondos_v1`, debemos:

1. **Copiar rutas a `fondos_app/urls.py`:**
   ```python
   # De publicaciones/urls.py y fondos/urls.py
   # A fondos_app/urls.py
   ```

2. **Asegurar que las rutas funcionen sin prefijo:**
   - Las rutas en `fondos_app/urls.py` deben empezar desde `/` (relativo)
   - El prefijo `/fondos/` se añade automáticamente en local vía `urls_root.py`

3. **Mantener nombres de URLs únicos:**
   - Usar prefijos en los nombres: `fondos_search`, `fondos_detail`, etc.
   - Evitar conflictos con otras apps

## 📋 Checklist

- [x] URLs root configuradas con prefijos para local
- [x] URLs por dominio configuradas sin prefijo
- [x] Middleware multi-dominio funcionando
- [x] Settings configurados correctamente
- [x] Dominio test.iccmu.es configurado
- [ ] Migrar URLs de fondos_v1 a fondos_app
- [ ] Probar en local con prefijos
- [ ] Probar simulando dominios en local
- [ ] Verificar en producción (fondos, madmusic, test)

