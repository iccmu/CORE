"""
Template tags personalizados para CMS
"""
from django import template
from wagtail.models import Page, Site
from wagtail.fields import RichTextField

register = template.Library()


@register.simple_tag(takes_context=True)
def menu_pages(context):
    """
    Obtiene las páginas hijas del root que tienen show_in_menus=True
    """
    request = context.get('request')
    if not request:
        return []
    
    try:
        # Obtener el site desde el request o desde el hostname
        site = None
        if hasattr(request, 'site'):
            site = request.site
        else:
            # Intentar obtener el site desde el hostname
            hostname = request.get_host().split(':')[0]
            site = Site.find_for_request(request)
        
        if site and site.root_page:
            # Obtener hijos directos que están publicados y marcados para menú
            menu_items = list(site.root_page.get_children().live().filter(show_in_menus=True))
            return menu_items
    except Exception:
        pass
    
    return []


@register.filter
def render_body(value):
    """
    Renderiza el body de una página: si es HTML plano usa safe, si no intenta richtext
    """
    if not value:
        return ""
    
    # Convertir a string
    body_str = str(value)
    
    # Si parece HTML plano (empieza con < y no es JSON), usar safe
    if body_str.strip().startswith('<') and not body_str.strip().startswith('{'):
        from django.utils.safestring import mark_safe
        return mark_safe(body_str)
    
    # Si no, intentar como richtext (para contenido editado desde Wagtail)
    # El filtro richtext de Wagtail maneja tanto HTML como bloques estructurados
    try:
        # Usar el filtro richtext de wagtailcore_tags
        from django.template import Context, Template
        from django.template.loader import get_template
        # Simplemente usar safe como fallback
        from django.utils.safestring import mark_safe
        return mark_safe(body_str)
    except:
        from django.utils.safestring import mark_safe
        return mark_safe(body_str)

