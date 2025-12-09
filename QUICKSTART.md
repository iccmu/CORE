# Quick Start - ICCMU Proyectos

## Activar entorno conda

```bash
conda activate core
```

## Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

El servidor estará disponible en: `http://127.0.0.1:8000/`

## Acceder a las aplicaciones

Desde la raíz (`http://127.0.0.1:8000/`) verás un índice automático con enlaces a todas las apps:

- `http://127.0.0.1:8000/` → Índice principal con todas las apps disponibles
- `http://127.0.0.1:8000/fondos/` → App de Fondos
- `http://127.0.0.1:8000/madmusic/` → App de Madmusic
- `http://127.0.0.1:8000/test/` → App de pruebas (JSON)

## Probar multi-dominio localmente

Para probar el sistema multi-dominio, añade estas líneas a `/etc/hosts`:

```
127.0.0.1 fondos.iccmu.es
127.0.0.1 madmusic.iccmu.es
127.0.0.1 test.iccmu.es
```

Luego accede a:
- `http://fondos.iccmu.es:8000/` → debería mostrar la página de Fondos (sin prefijo `/fondos/`)
- `http://madmusic.iccmu.es:8000/` → debería mostrar la página de Madmusic (sin prefijo `/madmusic/`)
- `http://test.iccmu.es:8000/` → debería mostrar la página de Test (sin prefijo `/test/`)
- `http://127.0.0.1:8000/` → Índice principal con todas las apps
- `http://127.0.0.1:8000/fondos/` → App Fondos (con prefijo en local)
- `http://127.0.0.1:8000/madmusic/` → App Madmusic (con prefijo en local)
- `http://127.0.0.1:8000/test/` → App Test (con prefijo en local)

## Crear superusuario (opcional)

```bash
python manage.py createsuperuser
```

Luego accede a `http://127.0.0.1:8000/admin/` para gestionar los modelos.

## Comandos útiles

```bash
# Verificar configuración
python manage.py check

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Shell de Django
python manage.py shell
```

