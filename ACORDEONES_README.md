# Sistema de Acordeones - MadMusic ICCMU

## 📋 Resumen de Implementación

Se ha implementado un sistema completo de acordeones Bootstrap para el sitio MadMusic, extrayendo el contenido del sitio original y replicando el estilo y funcionalidad.

## ✅ Componentes Implementados

### 1. Extractor de Contenido
**Archivo:** `scripts/extract_collapsibles.py`

Extrae 91 acordeones de 15 páginas HTML scrapeadas y los guarda en formato JSON estructurado.

**Uso:**
```bash
python scripts/extract_collapsibles.py
```

**Resultado:** Genera `data/collapsibles.json` con todo el contenido extraído.

### 2. Bloques de Wagtail
**Archivo:** `cms/blocks.py`

Implementa bloques StreamField para el CMS:
- `AccordionBlock` - Un acordeón individual
- `AccordionGroupBlock` - Grupo de acordeones
- `ImageWithCaptionBlock` - Imágenes con caption
- `QuoteBlock` - Citas destacadas

### 3. Templates HTML
**Archivos en:** `cms/templates/cms/blocks/`

- `accordion.html` - Template para acordeón individual
- `accordion_group.html` - Template para grupo de acordeones
- `image_with_caption.html` - Template para imágenes
- `quote.html` - Template para citas

### 4. Comando de Importación
**Archivo:** `cms/management/commands/import_collapsibles.py`

Importa acordeones desde JSON a páginas de Wagtail.

**Uso:**
```bash
# Ver qué se haría (dry-run)
python manage.py import_collapsibles --dry-run

# Importar todas las páginas
python manage.py import_collapsibles

# Importar una página específica
python manage.py import_collapsibles --page-slug servicios-e-infraestructura

# Forzar sobrescritura
python manage.py import_collapsibles --force
```

### 5. Estilos CSS
**Archivo:** `madmusic_app/static/madmusic/css/accordions.css`

Estilos completos replicados del sitio original, incluyendo:
- Animaciones de colapso/expansión
- Iconos de estado (chevron)
- Estilos hover y focus
- Responsive design
- Accesibilidad

## 🗂️ Páginas con Acordeones

### Páginas Prioritarias (ordenadas por número de acordeones):

1. **Publicaciones** (articulos-en-revistas-cientificas) - 25 acordeones
2. **Destacados MadMusic 1** (publicaciones-madmusic-2) - 12 acordeones
3. **Exposiciones | Eventos** (exposiciones) - 8 acordeones
4. **Conciertos | Grabaciones** (conciertos) - 8 acordeones
5. **Cuadernos de Música Iberoamericana** - 7 acordeones
6. **Fondos Documentales** (archivos) - 5 acordeones
7. **Cursos de Verano** - 5 acordeones
8. **Objetivos** - 4 acordeones
9. **Grupos Beneficiarios** - 3 acordeones
10. **Equipo** - 3 acordeones
11. **Congresos | Seminarios** - 3 acordeones
12. **Servicios e Infraestructura** - 2 acordeones
13. **Líneas de Investigación** - 2 acordeones
14. **Empleo** - 2 acordeones
15. **Participantes MadMusic 1** - 2 acordeones

## 🔄 Pasos para Usar el Sistema

### Paso 1: Preparar el Entorno

```bash
# Activar entorno virtual si es necesario
# source venv/bin/activate  # o el comando correspondiente

# Asegurar que las dependencias están instaladas
pip install beautifulsoup4 wagtail
```

### Paso 2: Crear las Migraciones

```bash
cd /Users/ivansimo/Documents/2025/UCM/ICCMU/CORE
python manage.py makemigrations cms
python manage.py migrate
```

### Paso 3: Crear las Páginas en Wagtail

Antes de importar acordeones, asegúrate de que las páginas existen en Wagtail:

1. Accede al admin: http://localhost:8000/admin/
2. Crea páginas StandardPage con los slugs correspondientes (ver mapeo abajo)
3. Deja el campo `body` vacío por ahora

### Paso 4: Importar Acordeones

```bash
# Probar primero con dry-run
python manage.py import_collapsibles --dry-run

# Si todo se ve bien, ejecutar la importación
python manage.py import_collapsibles
```

### Paso 5: Verificar en el Navegador

1. Inicia el servidor: `python manage.py runserver`
2. Visita las páginas con acordeones
3. Verifica que:
   - Los acordeones se expanden/colapsan correctamente
   - Los estilos se ven igual que en el sitio original
   - Las imágenes y enlaces funcionan
   - El comportamiento responsive funciona en móvil

## 📊 Mapeo de Páginas

| Archivo HTML | Slug de Página Wagtail |
|--------------|------------------------|
| servicios-e-infraestructura.html | servicios-e-infraestructura |
| transferencia/exposiciones.html | exposiciones-eventos |
| transferencia/conciertos.html | conciertos-grabaciones |
| proyecto-madmusic/objetivos.html | objetivos |
| proyecto-madmusic/investigacion.html | lineas-de-investigacion |
| formacion-empleo/empleo.html | empleo |
| equipo/participantes.html | participantes-madmusic-1 |
| equipo/grupos-beneficiarios.html | grupos-beneficiarios |
| equipo.html | equipo |
| divulgacion-cientifica/publicaciones-madmusic-2.html | destacados-madmusic-1 |
| divulgacion-cientifica/cuadernos-de-musica-iberoamericana.html | cuadernos-de-musica-iberoamericana |
| divulgacion-cientifica/congresos-madmusic.html | congresos-seminarios |
| divulgacion-cientifica/articulos-en-revistas-cientificas.html | publicaciones |
| divulgacion-cientifica/archivos.html | fondos-documentales |
| cursos-de-verano.html | cursos-de-verano |

## 🧪 Lista de Verificación

### Funcionalidad
- [ ] Los acordeones se expanden al hacer click
- [ ] Los acordeones se colapsan al hacer click nuevamente
- [ ] El icono de chevron rota correctamente
- [ ] Solo un acordeón abierto a la vez (cuando así está configurado)
- [ ] El contenido HTML se renderiza correctamente (imágenes, enlaces, listas)
- [ ] Las animaciones son suaves

### Estilos
- [ ] Los colores coinciden con el sitio original
- [ ] Las fuentes y tamaños son correctos
- [ ] El padding y spacing es consistente
- [ ] Los estados hover funcionan
- [ ] Los estados focus son visibles (accesibilidad)

### Responsive
- [ ] Los acordeones funcionan correctamente en móvil
- [ ] El texto se ajusta apropiadamente
- [ ] Los botones son fáciles de clickear en touch screens

### Contenido
- [ ] Todo el contenido HTML se preservó
- [ ] Las imágenes tienen las URLs correctas
- [ ] Los enlaces internos y externos funcionan
- [ ] Los estilos de texto (negrita, cursiva) se mantienen

## 🐛 Solución de Problemas

### Error: "No module named 'wagtail'"
**Solución:** Activar el entorno virtual o instalar Wagtail:
```bash
pip install wagtail
```

### Error: "Página no encontrada"
**Solución:** Crear la página en el admin de Wagtail primero con el slug correcto.

### Los acordeones no se abren/cierran
**Verificar:**
1. Bootstrap JS está cargado: `templates/madmusic/base.html` línea 715
2. jQuery está cargado antes de Bootstrap
3. El CSS de acordeones está incluido

### Los estilos no se aplican
**Verificar:**
1. `accordions.css` está referenciado en `base.html`
2. Los archivos estáticos se han recolectado: `python manage.py collectstatic`
3. El navegador no está cacheando CSS antiguo (Ctrl+Shift+R)

## 📝 Editar Acordeones en el Futuro

Los acordeones se pueden editar desde el admin de Wagtail:

1. Ir a `/admin/` y encontrar la página
2. En el campo "Body", verás el grupo de acordeones
3. Puedes:
   - Añadir nuevos acordeones
   - Editar títulos y contenido
   - Reordenar acordeones
   - Eliminar acordeones
   - Cambiar configuración (permitir múltiples abiertos, etc.)

## 🎨 Personalización

### Cambiar colores
Edita `madmusic_app/static/madmusic/css/accordions.css`:
- Color de fondo del heading: `.panel-heading { background-color: ... }`
- Color del borde: `.panel { border-color: ... }`
- Color de enlaces: `.panel-body a { color: ... }`

### Cambiar animación
Edita la duración en `accordions.css`:
```css
.panel-collapse {
    transition: height 0.35s ease; /* Cambiar 0.35s */
}
```

### Agregar iconos personalizados
Modifica el pseudo-elemento `:after` en `.panel-title > a`.

## 📚 Recursos Adicionales

- [Documentación de Wagtail StreamField](https://docs.wagtail.org/en/stable/topics/streamfield.html)
- [Bootstrap 3 Collapse](https://getbootstrap.com/docs/3.4/javascript/#collapse)
- [Sitio original de referencia](https://madmusic.iccmu.es/servicios-e-infraestructura/)

## ✨ Próximos Pasos Recomendados

1. **Crear páginas en Wagtail** con los slugs correctos
2. **Ejecutar migraciones** para aplicar cambios al modelo
3. **Importar acordeones** usando el comando management
4. **Verificar visualmente** cada página
5. **Ajustar estilos** si es necesario para coincidir exactamente con el original
6. **Agregar contenido adicional** usando el admin de Wagtail
