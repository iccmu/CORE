# ✅ Lista de Verificación - Sistema de Acordeones

## Estado de Implementación

### ✅ Completado

1. **Script Extractor** (`scripts/extract_collapsibles.py`)
   - ✅ Extrae 91 acordeones de 15 páginas HTML
   - ✅ Genera JSON estructurado en `data/collapsibles.json`
   - ✅ Preserva HTML interno completo
   - ✅ Detecta imágenes, enlaces y listas

2. **Bloques Wagtail** (`cms/blocks.py`)
   - ✅ AccordionBlock implementado
   - ✅ AccordionGroupBlock implementado
   - ✅ Soporte para configuración (múltiples abiertos, primer item abierto)
   - ✅ Bloques adicionales (ImageWithCaption, Quote)

3. **Templates HTML** (`cms/templates/cms/blocks/`)
   - ✅ accordion.html - Acordeón individual
   - ✅ accordion_group.html - Grupo de acordeones
   - ✅ image_with_caption.html - Imágenes
   - ✅ quote.html - Citas
   - ✅ Integración con Bootstrap collapse

4. **Modelo Wagtail** (`cms/models.py`)
   - ✅ StandardPage actualizado con StreamField
   - ✅ Soporte para múltiples tipos de bloques
   - ✅ Campo intro opcional
   - ✅ Template actualizado para renderizar StreamField

5. **Comando de Importación** (`cms/management/commands/import_collapsibles.py`)
   - ✅ Importación automática desde JSON
   - ✅ Mapeo de páginas HTML a slugs
   - ✅ Modo dry-run para testing
   - ✅ Limpieza de HTML para compatibilidad
   - ✅ Opción --force para sobrescribir

6. **Estilos CSS** (`madmusic_app/static/madmusic/css/accordions.css`)
   - ✅ Estilos completos de Bootstrap panels
   - ✅ Animaciones de colapso/expansión
   - ✅ Iconos de estado (chevron)
   - ✅ Estados hover y focus
   - ✅ Responsive design
   - ✅ Accesibilidad

7. **Integración** (`templates/madmusic/base.html`)
   - ✅ CSS de acordeones incluido
   - ✅ Bootstrap JS disponible
   - ✅ jQuery cargado

## 📋 Pasos Siguientes para el Usuario

### 1. Preparación del Entorno
```bash
# Activar entorno virtual (si aplica)
source venv/bin/activate

# Instalar dependencias si falta alguna
pip install beautifulsoup4
```

### 2. Aplicar Migraciones de Django
```bash
cd /Users/ivansimo/Documents/2025/UCM/ICCMU/CORE
python manage.py makemigrations cms
python manage.py migrate
```

**Nota:** Es posible que necesites activar el entorno virtual donde está instalado Wagtail.

### 3. Crear Páginas en Wagtail Admin

Accede a http://localhost:8000/admin/ y crea páginas StandardPage con estos slugs:

**Páginas prioritarias para empezar:**
1. `servicios-e-infraestructura` (2 acordeones)
2. `exposiciones-eventos` (8 acordeones)
3. `objetivos` (4 acordeones)

**Todas las páginas:**
- servicios-e-infraestructura
- exposiciones-eventos
- conciertos-grabaciones
- objetivos
- lineas-de-investigacion
- empleo
- participantes-madmusic-1
- grupos-beneficiarios
- equipo
- destacados-madmusic-1
- cuadernos-de-musica-iberoamericana
- congresos-seminarios
- publicaciones
- fondos-documentales
- cursos-de-verano

### 4. Importar Acordeones

```bash
# Primero, prueba con dry-run para ver qué pasará
python manage.py import_collapsibles --dry-run

# Si todo se ve bien, importa todo
python manage.py import_collapsibles

# O importa página por página
python manage.py import_collapsibles --page-slug servicios-e-infraestructura
```

### 5. Verificar Funcionalidad

1. **Iniciar servidor:** `python manage.py runserver`
2. **Visitar página:** http://localhost:8000/madmusic/servicios-e-infraestructura/
3. **Probar acordeones:**
   - Click en título → se expande
   - Click nuevamente → se colapsa
   - Verificar contenido HTML completo
   - Verificar imágenes y enlaces

### 6. Verificaciones Visuales

Comparar con el sitio original: https://madmusic.iccmu.es/servicios-e-infraestructura/

**Checklist visual:**
- [ ] Colores de fondo coinciden
- [ ] Bordes y sombras correctos
- [ ] Tipografía igual (tamaño, peso)
- [ ] Espaciado consistente
- [ ] Iconos de chevron visibles y animados
- [ ] Hover states funcionan
- [ ] Contenido HTML renderizado correctamente

### 7. Pruebas Responsive

- [ ] Desktop (>1200px)
- [ ] Tablet (768px - 1200px)
- [ ] Móvil (<768px)
- [ ] Touch events funcionan en móvil

## 🎯 Páginas de Ejemplo para Probar

### Caso Simple (Comenzar aquí)
**Página:** Servicios e Infraestructura
- Solo 2 acordeones grandes
- Contenido mixto (texto, listas, blockquotes)
- Buen caso de prueba inicial

### Caso Intermedio
**Página:** Exposiciones | Eventos
- 8 acordeones
- Incluye imágenes
- Múltiples enlaces externos
- Formato variado

### Caso Complejo
**Página:** Publicaciones (articulos-en-revistas-cientificas)
- 25 acordeones
- Mucho contenido
- Lista extensa
- Mejor para testing de rendimiento

## 🐛 Problemas Conocidos y Soluciones

### Si las migraciones fallan
**Error:** ModuleNotFoundError: No module named 'wagtail'

**Solución:**
```bash
# Verificar que Wagtail está instalado
pip list | grep -i wagtail

# Si no está, instalar
pip install wagtail

# O activar el entorno virtual correcto
```

### Si los acordeones no se abren
**Causa:** Bootstrap JS no está cargado o hay conflicto con jQuery

**Verificar:**
1. Abrir DevTools Console
2. Buscar errores de JavaScript
3. Verificar que jQuery se carga antes de Bootstrap
4. Verificar ruta de bootstrap.min.js

### Si los estilos no se aplican
**Solución:**
```bash
# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Limpiar caché del navegador
# Chrome/Firefox: Ctrl+Shift+R
```

## 📊 Resumen de Archivos Creados

```
CORE/
├── scripts/
│   └── extract_collapsibles.py          [NUEVO]
├── data/
│   └── collapsibles.json                [GENERADO]
├── cms/
│   ├── blocks.py                        [NUEVO]
│   ├── models.py                        [MODIFICADO]
│   ├── templates/cms/
│   │   ├── blocks/
│   │   │   ├── accordion.html           [NUEVO]
│   │   │   ├── accordion_group.html     [NUEVO]
│   │   │   ├── image_with_caption.html  [NUEVO]
│   │   │   └── quote.html               [NUEVO]
│   │   └── standard_page.html           [MODIFICADO]
│   └── management/
│       ├── __init__.py                  [NUEVO]
│       └── commands/
│           ├── __init__.py              [NUEVO]
│           └── import_collapsibles.py   [NUEVO]
├── madmusic_app/static/madmusic/css/
│   └── accordions.css                   [NUEVO]
├── templates/madmusic/
│   └── base.html                        [MODIFICADO]
├── ACORDEONES_README.md                 [NUEVO]
└── VERIFICATION_CHECKLIST.md            [NUEVO]
```

## ✨ Todo Listo Para Usar

El sistema está completamente implementado y listo para:
1. Aplicar migraciones
2. Crear páginas en Wagtail
3. Importar acordeones
4. Verificar visualmente
5. Comenzar a usar

**Documentación completa:** Ver `ACORDEONES_README.md` para instrucciones detalladas.
