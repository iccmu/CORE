# Estándares y Pruebas - ICCMU Proyectos

## 📋 Índice

1. [Estándares Web](#estándares-web)
2. [SEO (Search Engine Optimization)](#seo)
3. [Sistemas Ontológicos](#sistemas-ontológicos)
4. [Gestión de Usuarios y Permisos](#gestión-de-usuarios-y-permisos)

---

## 🌐 Estándares Web

### Checklist de Estándares Web

#### HTML5 y Semántica
- [ ] Usar elementos semánticos HTML5 (`<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<footer>`)
- [ ] Estructura jerárquica correcta de headings (`h1` → `h2` → `h3`)
- [ ] Un solo `<h1>` por página
- [ ] Atributos `alt` en todas las imágenes
- [ ] Atributos `lang` en elementos HTML (`<html lang="es">`)
- [ ] Meta charset UTF-8
- [ ] Viewport meta tag para responsive design

#### Accesibilidad (WCAG 2.1)
- [ ] Contraste de colores mínimo 4.5:1 para texto normal, 3:1 para texto grande
- [ ] Navegación por teclado funcional (Tab, Enter, Esc)
- [ ] Skip links para saltar navegación
- [ ] Labels asociados a todos los inputs
- [ ] ARIA labels donde sea necesario
- [ ] Focus visible en elementos interactivos
- [ ] Textos alternativos descriptivos
- [ ] Formularios accesibles con mensajes de error claros

#### Responsive Design
- [ ] Diseño mobile-first
- [ ] Breakpoints estándar: mobile (320px+), tablet (768px+), desktop (1024px+)
- [ ] Imágenes responsive (`srcset`, `sizes`)
- [ ] Menús adaptativos (hamburger en mobile)
- [ ] Tablas scrollables en mobile
- [ ] Touch targets mínimo 44x44px

#### Performance
- [ ] Minificación de CSS y JavaScript
- [ ] Compresión Gzip/Brotli habilitada
- [ ] Lazy loading de imágenes
- [ ] Caché de recursos estáticos
- [ ] CDN para assets estáticos (opcional)
- [ ] Optimización de imágenes (WebP, formato adecuado)
- [ ] Tiempo de carga < 3 segundos
- [ ] Lighthouse score > 90

#### Seguridad Web
- [ ] HTTPS habilitado en producción
- [ ] Headers de seguridad (CSP, X-Frame-Options, X-Content-Type-Options)
- [ ] CSRF protection en formularios Django
- [ ] Validación de inputs (server-side y client-side)
- [ ] Sanitización de datos de usuario
- [ ] Rate limiting en APIs
- [ ] SQL injection prevention (usar ORM de Django)
- [ ] XSS prevention (escapado automático en templates)

#### Estándares de Código
- [ ] Validación HTML (W3C Validator)
- [ ] Validación CSS (W3C CSS Validator)
- [ ] JavaScript sin errores en consola
- [ ] Código semántico y bien estructurado
- [ ] Comentarios en código complejo

---

## 🔍 SEO (Search Engine Optimization)

### Checklist SEO Técnico

#### Meta Tags Esenciales
- [ ] `<title>` único y descriptivo por página (50-60 caracteres)
- [ ] Meta description única por página (150-160 caracteres)
- [ ] Meta keywords (opcional, menos importante ahora)
- [ ] Open Graph tags para redes sociales
  - `og:title`, `og:description`, `og:image`, `og:url`, `og:type`
- [ ] Twitter Card tags
- [ ] Canonical URLs para evitar contenido duplicado
- [ ] Meta robots (index/noindex, follow/nofollow)

#### Estructura de URLs
- [ ] URLs amigables y descriptivas (`/fondos/edicion/123/` vs `/p?id=123`)
- [ ] URLs en español (o idioma correspondiente)
- [ ] Sin parámetros innecesarios en URLs
- [ ] Estructura jerárquica lógica
- [ ] URLs cortas pero descriptivas
- [ ] Guiones en lugar de guiones bajos (`fondos-historicos` vs `fondos_historicos`)

#### Sitemap y Robots.txt
- [ ] Sitemap.xml generado automáticamente (Django `sitemap` framework)
- [ ] Robots.txt configurado correctamente
- [ ] Sitemap incluido en Google Search Console
- [ ] Sitemap actualizado automáticamente al crear contenido

#### Schema.org / JSON-LD
- [ ] Schema.org markup para contenido estructurado
- [ ] JSON-LD para datos estructurados
- [ ] Schemas relevantes:
  - `CollectionPage` para catálogos
  - `Book` / `MusicComposition` para ediciones
  - `Organization` para ICCMU
  - `BreadcrumbList` para navegación
  - `Person` para autores
  - `CreativeWork` para publicaciones

#### Contenido SEO-Friendly
- [ ] Contenido único y de calidad
- [ ] Keywords naturales en contenido (no keyword stuffing)
- [ ] Headings con keywords relevantes
- [ ] Enlaces internos relevantes
- [ ] Enlaces externos a fuentes autorizadas
- [ ] Contenido actualizado regularmente
- [ ] Longitud adecuada de contenido (>300 palabras para páginas importantes)

#### Performance SEO
- [ ] Core Web Vitals optimizados:
  - LCP (Largest Contentful Paint) < 2.5s
  - FID (First Input Delay) < 100ms
  - CLS (Cumulative Layout Shift) < 0.1
- [ ] Mobile-friendly (Google Mobile-Friendly Test)
- [ ] Página rápida (PageSpeed Insights)

#### Internacionalización (i18n)
- [ ] Hreflang tags si hay múltiples idiomas
- [ ] Idioma correcto en `<html lang="es">`
- [ ] URLs por idioma si aplica (`/es/`, `/en/`)

---

## 🧠 Sistemas Ontológicos

### Checklist Sistemas Ontológicos

#### Modelado de Datos
- [ ] Modelos Django bien estructurados y normalizados
- [ ] Relaciones entre modelos claras y bien definidas
- [ ] Campos con tipos de datos apropiados
- [ ] Constraints y validaciones en modelos
- [ ] Índices en campos de búsqueda frecuente
- [ ] Foreign keys con `on_delete` apropiado

#### Vocabularios Controlados
- [ ] Vocabularios controlados para campos clave:
  - Tipos de documentos (manuscrito/impreso)
  - Idiomas (ISO 639-1 o 639-2)
  - Formatos estándar
  - Materias/temas (vocabulario controlado)
- [ ] Choices en Django models para valores limitados
- [ ] Tablas de referencia para vocabularios extensos

#### Identificadores Únicos
- [ ] Identificadores persistentes (UUIDs o IDs estables)
- [ ] DOIs para publicaciones si aplica
- [ ] Identificadores canónicos para autores (VIAF, ISNI)
- [ ] Signaturas únicas para documentos

#### Metadatos Ricos
- [ ] Metadatos Dublin Core básicos:
  - Title (dc:title)
  - Creator (dc:creator)
  - Subject (dc:subject)
  - Description (dc:description)
  - Publisher (dc:publisher)
  - Date (dc:date)
  - Type (dc:type)
  - Format (dc:format)
  - Identifier (dc:identifier)
- [ ] Metadatos específicos del dominio (música, fondos documentales)
- [ ] Metadatos técnicos (formato, tamaño, resolución)

#### Relaciones Semánticas
- [ ] Relaciones explícitas entre entidades:
  - Autor → Obra
  - Obra → Edición
  - Edición → Ejemplar
  - Documento → Colección/Fondo
- [ ] Relaciones Many-to-Many bien modeladas
- [ ] Relaciones jerárquicas (padre-hijo) si aplica

#### Búsqueda Semántica
- [ ] Búsqueda por sinónimos y variantes
- [ ] Búsqueda por relaciones (encontrar obras de un autor)
- [ ] Búsqueda facetada (por tipo, fecha, formato, etc.)
- [ ] Autocompletado inteligente
- [ ] Búsqueda con corrección ortográfica
- [ ] Búsqueda multilingüe si aplica

#### Linked Data / RDF
- [ ] Considerar exportación RDF/JSON-LD
- [ ] URIs persistentes para recursos
- [ ] Enlaces a datos externos (DBpedia, Wikidata, VIAF)
- [ ] Vocabularios estándar (FOAF, BIBO, FRBR)

#### APIs Semánticas
- [ ] API RESTful bien diseñada
- [ ] Documentación de API (OpenAPI/Swagger)
- [ ] Versionado de API
- [ ] Respuestas en múltiples formatos (JSON, XML, RDF)

---

## 👥 Gestión de Usuarios y Permisos

### Checklist Gestión de Usuarios

#### Autenticación
- [ ] Sistema de autenticación Django estándar o personalizado
- [ ] Login seguro (CSRF protection, rate limiting)
- [ ] Logout funcional
- [ ] Recuperación de contraseña
- [ ] Cambio de contraseña
- [ ] Registro de usuarios (si aplica)
- [ ] Verificación de email (si aplica)
- [ ] Autenticación de dos factores (2FA) - recomendado para admins

#### Modelo de Usuario
- [ ] Extender modelo User de Django si es necesario
- [ ] Campos adicionales relevantes (perfil, organización, etc.)
- [ ] Relaciones con otros modelos si aplica
- [ ] Historial de actividad del usuario

#### Grupos y Permisos
- [ ] Grupos de usuarios definidos:
  - Administradores
  - Editores/Colaboradores
  - Usuarios registrados
  - Usuarios anónimos
- [ ] Permisos granulares por app/modelo:
  - `fondos_app.add_edicion`
  - `fondos_app.change_edicion`
  - `fondos_app.delete_edicion`
  - `fondos_app.view_edicion`
- [ ] Permisos personalizados si es necesario
- [ ] Asignación de permisos a grupos

#### Control de Acceso
- [ ] Decoradores `@login_required` en vistas protegidas
- [ ] `@permission_required` para permisos específicos
- [ ] Mixins de permisos en class-based views
- [ ] Verificación de permisos en templates (`{% if perms.app.action_model %}`)
- [ ] Control de acceso a nivel de objeto (si aplica)

#### Roles Específicos del Proyecto
- [ ] **Catalogadores**: Pueden crear/editar ediciones
- [ ] **Revisores**: Pueden revisar y aprobar ediciones
- [ ] **Administradores**: Acceso completo
- [ ] **Investigadores**: Solo lectura avanzada
- [ ] **Público**: Solo lectura básica

#### Seguridad de Usuarios
- [ ] Contraseñas seguras (validación de complejidad)
- [ ] Encriptación de contraseñas (Django lo hace automáticamente)
- [ ] Sesiones seguras (configuración de `SESSION_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`)
- [ ] Timeout de sesión
- [ ] Registro de intentos de login fallidos
- [ ] Bloqueo de cuenta después de intentos fallidos

#### Gestión de Usuarios en Admin
- [ ] Interfaz admin personalizada para usuarios
- [ ] Filtros útiles en admin de usuarios
- [ ] Acciones masivas para gestión de usuarios
- [ ] Exportación de datos de usuarios (si aplica)

#### Auditoría
- [ ] Registro de acciones de usuarios (quién hizo qué y cuándo)
- [ ] Historial de cambios en modelos importantes
- [ ] Logs de acceso y actividad
- [ ] Trazabilidad de modificaciones

#### Integración con Sistemas Externos
- [ ] SSO (Single Sign-On) si aplica
- [ ] Integración con LDAP/Active Directory si aplica
- [ ] OAuth2 para APIs si aplica

---

## 🧪 Plan de Pruebas

### Pruebas Automatizadas Recomendadas

#### Tests Unitarios
```python
# Ejemplo estructura de tests
tests/
├── test_models.py          # Tests de modelos
├── test_views.py           # Tests de vistas
├── test_forms.py          # Tests de formularios
├── test_permissions.py    # Tests de permisos
├── test_search.py         # Tests de búsqueda
└── test_api.py            # Tests de API
```

#### Tests de Integración
- [ ] Flujo completo de creación de edición
- [ ] Flujo de búsqueda y filtrado
- [ ] Flujo de autenticación y autorización
- [ ] Flujo de migración de datos

#### Tests de Rendimiento
- [ ] Tests de carga (carga de página < 3s)
- [ ] Tests de búsqueda (tiempo de respuesta < 1s)
- [ ] Tests de concurrencia (múltiples usuarios simultáneos)

#### Tests de Accesibilidad
- [ ] Tests automatizados con axe-core o similar
- [ ] Tests manuales con lectores de pantalla
- [ ] Tests de navegación por teclado

---

## 📊 Herramientas Recomendadas

### Desarrollo
- **Linting**: flake8, pylint, black (formateo)
- **Testing**: pytest, pytest-django
- **Coverage**: coverage.py (objetivo > 80%)

### SEO
- **Google Search Console**: Monitoreo y optimización
- **Google Analytics**: Análisis de tráfico
- **Schema.org Validator**: Validar structured data
- **PageSpeed Insights**: Performance
- **Lighthouse**: Auditoría completa

### Accesibilidad
- **axe DevTools**: Extension de navegador
- **WAVE**: Web Accessibility Evaluation Tool
- **NVDA/JAWS**: Lectores de pantalla para testing

### Performance
- **Django Debug Toolbar**: Debugging en desarrollo
- **django-silk**: Profiling de queries
- **New Relic / Sentry**: Monitoreo en producción

---

## ✅ Checklist de Implementación Prioritaria

### Fase 1: Fundamentos (Ahora)
- [ ] Estructura HTML semántica
- [ ] Meta tags básicos (title, description)
- [ ] Modelos Django bien estructurados
- [ ] Sistema de autenticación básico
- [ ] Permisos básicos configurados

### Fase 2: SEO y Accesibilidad
- [ ] Schema.org markup
- [ ] Sitemap.xml
- [ ] Robots.txt
- [ ] Accesibilidad básica (WCAG AA)
- [ ] Performance optimizado

### Fase 3: Avanzado
- [ ] Vocabularios controlados completos
- [ ] Búsqueda semántica avanzada
- [ ] Permisos granulares
- [ ] Auditoría y logs
- [ ] APIs documentadas

---

## 📝 Notas

- Priorizar estándares web y SEO desde el inicio
- Los sistemas ontológicos mejoran la calidad de los datos y la búsqueda
- La gestión de usuarios debe ser segura pero no restrictiva para usuarios legítimos
- Documentar decisiones importantes sobre estructura de datos y permisos



