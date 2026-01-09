"""
Template tags personalizados para CMS
"""
from django import template
from wagtail.models import Page, Site
from wagtail.fields import RichTextField

register = template.Library()


def get_menu_items(parent_page, current_page=None, max_depth=2, include_children=True):
    """
    Obtiene recursivamente las páginas del menú con sus hijos
    
    Args:
        parent_page: Página padre
        current_page: Página actual (para marcar activa)
        max_depth: Profundidad máxima del menú
        include_children: Si True, incluye hijos aunque no tengan show_in_menus=True
    """
    menu_items = []
    
    # Obtener hijos directos que están publicados y marcados para menú
    children = parent_page.get_children().live().filter(show_in_menus=True)
    
    for child in children:
        # Usar Page base para is_ancestor_of, pero specific() para el resto
        child_specific = child.specific
        
        # Verificar si es ancestro: current_page está debajo de child en el árbol
        is_ancestor = False
        if current_page:
            try:
                # Obtener Page base para la comparación
                child_page = Page.objects.get(id=child.id)
                current_page_base = Page.objects.get(id=current_page.id) if hasattr(current_page, 'id') else None
                if current_page_base:
                    # En Wagtail, una página es ancestro si el path de la página actual empieza con el path del ancestro
                    # y no son la misma página
                    is_ancestor = (
                        current_page_base.path.startswith(child_page.path) and 
                        current_page_base.id != child_page.id
                    )
            except Exception:
                pass
        
        item = {
            'page': child_specific,
            'title': child_specific.title,
            'url': child_specific.url,
            'is_current': current_page and (child.id == current_page.id),
            'is_ancestor': is_ancestor,
            'children': [],
        }
        
        # Si no hemos alcanzado el máximo de profundidad, obtener hijos
        # Para submenús, incluimos todos los hijos aunque no tengan show_in_menus=True
        if max_depth > 1:
            # Obtener todos los hijos vivos para submenús
            sub_children = child.get_children().live()
            for sub_child in sub_children:
                sub_child_specific = sub_child.specific
                
                sub_item = {
                    'page': sub_child_specific,
                    'title': sub_child_specific.title,
                    'url': sub_child_specific.url,
                    'is_current': current_page and (sub_child.id == current_page.id),
                    'is_ancestor': False,  # Los hijos de nivel 2 no tienen ancestros en este menú
                    'children': [],
                }
                # Si hay más profundidad, obtener nietos también
                if max_depth > 2:
                    sub_item['children'] = get_menu_items(sub_child, current_page, max_depth - 1, include_children=False)
                item['children'].append(sub_item)
        
        menu_items.append(item)
    
    return menu_items


def _get_wagtail_menu_items(current_page=None, max_depth=2):
    """
    Función auxiliar para obtener items del menú
    """
    menu_items = []
    try:
        from cms.models import HomePage
        home_page = HomePage.objects.filter(slug='madmusic-home').first()
        if home_page:
            menu_items = get_menu_items(home_page, current_page, max_depth)
    except Exception:
        pass
    return menu_items if menu_items else []


@register.inclusion_tag('cms/menu.html', takes_context=True)
def wagtail_menu(context, max_depth=2):
    """
    Genera el menú principal de navegación desde Wagtail
    """
    current_page = context.get('page')
    
    # Obtener items del menú directamente (no depende del request)
    menu_items = _get_wagtail_menu_items(current_page, max_depth)
    
    # Asegurarse de que siempre devolvemos un dict con menu_items (nunca None)
    return {
        'menu_items': menu_items,
        'current_page': current_page,
    }


@register.simple_tag(takes_context=True)
def wagtail_menu_html(context, max_depth=2):
    """
    Versión alternativa que renderiza el HTML directamente (fallback)
    """
    from django.template.loader import render_to_string
    current_page = context.get('page')
    menu_items = _get_wagtail_menu_items(current_page, max_depth)
    
    return render_to_string('cms/menu.html', {
        'menu_items': menu_items,
        'current_page': current_page,
    })


@register.simple_tag(takes_context=True)
def menu_pages(context):
    """
    Obtiene las páginas hijas del root que tienen show_in_menus=True
    (Mantenido para compatibilidad)
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

