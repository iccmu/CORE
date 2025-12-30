"""
Context processors para CMS
"""
from cms.templatetags.cms_tags import _get_wagtail_menu_items


def wagtail_menu_context(request):
    """
    Context processor que añade el menú de Wagtail al contexto
    """
    # Intentar obtener la página actual del contexto de Wagtail
    current_page = None
    if hasattr(request, 'site'):
        # Wagtail puede tener la página en request.site
        pass
    
    # Obtener items del menú
    menu_items = _get_wagtail_menu_items(current_page, max_depth=2)
    
    return {
        'wagtail_menu_items': menu_items,
    }

