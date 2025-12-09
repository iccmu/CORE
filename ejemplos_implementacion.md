# Ejemplos de Implementación - Estándares

## 🎯 Ejemplos Prácticos para Empezar

### 1. Template Base con SEO

**Archivo:** `templates/base/base_seo.html`

```django
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    {# Meta tags dinámicos #}
    <title>{% block title %}{{ page_title|default:"ICCMU Proyectos" }}{% endblock %}</title>
    <meta name="description" content="{% block meta_description %}{{ meta_description|default:"Catálogo de fondos documentales del ICCMU" }}{% endblock %}">
    <meta name="keywords" content="{% block meta_keywords %}música, fondos documentales, ICCMU{% endblock %}">
    
    {# Canonical URL #}
    <link rel="canonical" href="{% block canonical_url %}{{ request.build_absolute_uri }}{% endblock %}">
    
    {# Open Graph #}
    <meta property="og:title" content="{% block og_title %}{{ page_title|default:"ICCMU Proyectos" }}{% endblock %}">
    <meta property="og:description" content="{% block og_description %}{{ meta_description|default:"Catálogo de fondos documentales del ICCMU" }}{% endblock %}">
    <meta property="og:type" content="{% block og_type %}website{% endblock %}">
    <meta property="og:url" content="{{ request.build_absolute_uri }}">
    <meta property="og:image" content="{% block og_image %}{{ request.build_absolute_uri }}{% static 'images/og-image.jpg' %}{% endblock %}">
    
    {# Schema.org JSON-LD #}
    {% block schema_org %}{% endblock %}
    
    {# CSS #}
    {% block extra_css %}{% endblock %}
</head>
<body>
    <a href="#main-content" class="skip-link">Saltar al contenido principal</a>
    
    <header role="banner">
        {% block header %}{% endblock %}
    </header>
    
    <nav role="navigation" aria-label="Navegación principal">
        {% block navigation %}{% endblock %}
    </nav>
    
    <main id="main-content" role="main">
        {% block content %}{% endblock %}
    </main>
    
    <footer role="contentinfo">
        {% block footer %}{% endblock %}
    </footer>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### 2. Schema.org para Edición

**En template de detalle de edición:**

```django
{% extends "base/base_seo.html" %}

{% block schema_org %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Book",
  "name": "{{ edicion.titulo_propio }}",
  "author": {
    "@type": "Person",
    "name": "{{ edicion.autor_uniforme }}"
  },
  "publisher": {
    "@type": "Organization",
    "name": "ICCMU"
  },
  "datePublished": "{{ edicion.fecha_documento }}",
  "inLanguage": "{{ edicion.idioma }}",
  "identifier": "{{ edicion.signatura }}",
  "description": "{{ edicion.descripcion_fisica }}"
}
</script>
{% endblock %}
```

### 3. Vocabularios Controlados

**Archivo:** `core/vocabularies.py`

```python
# Vocabularios controlados para el proyecto

TIPOS_DOCUMENTO = [
    ('manuscrito', 'Música manuscrita'),
    ('impreso', 'Música impresa'),
]

IDIOMAS = [
    ('es', 'Español'),
    ('en', 'Inglés'),
    ('fr', 'Francés'),
    ('it', 'Italiano'),
    ('de', 'Alemán'),
    ('la', 'Latín'),
]

FORMATOS = [
    ('partitura', 'Partitura'),
    ('partitura_orquestal', 'Partitura orquestal'),
    ('partitura_reduccion', 'Reducción'),
    ('parte', 'Parte'),
]

MATERIAS = [
    ('musica_religiosa', 'Música religiosa'),
    ('musica_profana', 'Música profana'),
    ('opera', 'Ópera'),
    ('zarzuela', 'Zarzuela'),
    ('sinfonia', 'Sinfonía'),
    # ... más materias
]
```

**Uso en modelo:**

```python
from django.db import models
from core.vocabularies import TIPOS_DOCUMENTO, IDIOMAS

class Edicion(models.Model):
    # ...
    tipo_documento = models.CharField(
        max_length=20,
        choices=TIPOS_DOCUMENTO,
        blank=True
    )
    idioma = models.CharField(
        max_length=10,
        choices=IDIOMAS,
        blank=True
    )
```

### 4. Permisos Personalizados

**Archivo:** `fondos_app/permissions.py`

```python
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import Edicion

def create_custom_permissions():
    """Crear permisos personalizados para fondos_app"""
    content_type = ContentType.objects.get_for_model(Edicion)
    
    permissions = [
        ('can_approve_edicion', 'Puede aprobar ediciones'),
        ('can_publish_edicion', 'Puede publicar ediciones'),
        ('can_view_restricted', 'Puede ver contenido restringido'),
    ]
    
    for codename, name in permissions:
        Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=content_type,
        )
```

**Uso en vista:**

```python
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render

@permission_required('fondos_app.can_approve_edicion')
def approve_edicion(request, id):
    # Lógica de aprobación
    pass
```

### 5. Búsqueda Semántica Mejorada

**Archivo:** `fondos_app/search.py`

```python
from django.db.models import Q
from unidecode import unidecode

class SemanticSearch:
    """Búsqueda semántica con sinónimos y variantes"""
    
    SINONIMOS = {
        'autor': ['compositor', 'creador', 'músico'],
        'obra': ['composición', 'pieza', 'trabajo'],
        'partitura': ['partitura', 'score', 'partitura general'],
    }
    
    @classmethod
    def expand_query(cls, query):
        """Expande la query con sinónimos"""
        query_terms = query.lower().split()
        expanded_terms = []
        
        for term in query_terms:
            expanded_terms.append(term)
            # Añadir sinónimos
            for key, synonyms in cls.SINONIMOS.items():
                if term in synonyms or term == key:
                    expanded_terms.extend(synonyms)
        
        return ' '.join(set(expanded_terms))  # Eliminar duplicados
    
    @classmethod
    def build_search_query(cls, query, model_fields):
        """Construye query de búsqueda con expansión semántica"""
        expanded_query = cls.expand_query(query)
        query_normalized = unidecode(expanded_query)
        
        lookups = Q()
        for field in model_fields:
            lookups |= Q(**{f"{field}__icontains": query_normalized})
        
        return lookups
```

**Uso en vista:**

```python
from .search import SemanticSearch

def post_search_view(request):
    query = request.GET.get('q')
    if query:
        fields = ['titulo_propio', 'titulo_uniforme', 'autor_uniforme']
        lookups = SemanticSearch.build_search_query(query, fields)
        qs = Edicion.objects.filter(lookups)
    else:
        qs = Edicion.objects.all()
    # ...
```

### 6. Sitemap.xml

**Archivo:** `fondos_app/sitemaps.py`

```python
from django.contrib.sitemaps import Sitemap
from .models import Edicion

class EdicionSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8
    
    def items(self):
        return Edicion.objects.filter(publicado=True)
    
    def lastmod(self, obj):
        return obj.fecha_modificacion
    
    def location(self, obj):
        return f'/fondos/{obj.id}/'
```

**En `proyectos/urls_root.py`:**

```python
from django.contrib.sitemaps.views import sitemap
from fondos_app.sitemaps import EdicionSitemap

sitemaps = {
    'ediciones': EdicionSitemap,
}

urlpatterns = [
    # ...
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
]
```

### 7. Robots.txt

**Archivo:** `templates/robots.txt`

```
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /staticfiles/

Sitemap: https://fondos.iccmu.es/sitemap.xml
Sitemap: https://madmusic.iccmu.es/sitemap.xml
```

**En `proyectos/urls_root.py`:**

```python
from django.http import HttpResponse
from django.template.loader import render_to_string

def robots_txt(request):
    template = 'robots.txt'
    context = {}
    return HttpResponse(
        render_to_string(template, context),
        content_type='text/plain'
    )

urlpatterns = [
    path('robots.txt', robots_txt),
    # ...
]
```

### 8. Accesibilidad - Skip Link

**En CSS:**

```css
.skip-link {
    position: absolute;
    top: -40px;
    left: 0;
    background: #000;
    color: #fff;
    padding: 8px;
    text-decoration: none;
    z-index: 100;
}

.skip-link:focus {
    top: 0;
}
```

### 9. Tests de Permisos

**Archivo:** `fondos_app/tests/test_permissions.py`

```python
from django.test import TestCase
from django.contrib.auth.models import User, Permission
from .models import Edicion

class PermissionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.edicion = Edicion.objects.create(
            signatura='TEST-001',
            titulo_propio='Test',
            # ... otros campos
        )
    
    def test_user_can_view_edicion(self):
        """Usuario puede ver ediciones públicas"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/fondos/{self.edicion.id}/')
        self.assertEqual(response.status_code, 200)
    
    def test_user_cannot_approve_without_permission(self):
        """Usuario sin permiso no puede aprobar"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/fondos/{self.edicion.id}/approve/')
        self.assertEqual(response.status_code, 403)
    
    def test_user_can_approve_with_permission(self):
        """Usuario con permiso puede aprobar"""
        permission = Permission.objects.get(codename='can_approve_edicion')
        self.user.user_permissions.add(permission)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/fondos/{self.edicion.id}/approve/')
        self.assertEqual(response.status_code, 200)
```

## 🚀 Próximos Pasos

1. Implementar template base con SEO
2. Crear vocabularios controlados
3. Añadir Schema.org a modelos principales
4. Configurar sitemap.xml
5. Implementar permisos básicos
6. Crear tests de permisos

