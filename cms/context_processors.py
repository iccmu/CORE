"""
Context processors para CMS
"""
from cms.templatetags.cms_tags import get_menu_items


def wagtail_menu_context(request):
    """
    Context processor que añade el menú de Wagtail al contexto
    Genera dos niveles:
    - primary_menu: menú principal (barra blanca) con submenús para hover
    - secondary_menu: submenú del item activo (barra roja)
    """
    # Detectar página actual
    current_page = None
    
    # 1. Si es una vista de Wagtail, usar page del request
    if hasattr(request, 'page'):
        current_page = request.page
    
    # 2. Si es una vista Django, intentar mapear por path
    if not current_page:
        try:
            from cms.models import StandardPage, NewsIndexPage, HomePage
            from wagtail.models import Page
            
            # Limpiar path (ej: /madmusic/equipo/ -> equipo)
            path = request.path.strip('/')
            if path.startswith('madmusic/'):
                slug = path.replace('madmusic/', '').strip('/')
                
                # Buscar página por slug
                home_page = HomePage.objects.filter(slug='madmusic-home').first()
                if home_page and slug:
                    # Buscar por el último segmento del slug
                    slug_part = slug.split('/')[-1] if '/' in slug else slug
                    
                    # Intentar buscar como descendiente de home
                    possible_pages = Page.objects.descendant_of(home_page).filter(slug=slug_part).live().specific()
                    
                    # Si encontramos múltiples, intentar match exacto por url_path
                    if possible_pages.count() > 1:
                        for page in possible_pages:
                            if slug in page.url_path:
                                current_page = page
                                break
                    elif possible_pages.count() == 1:
                        current_page = possible_pages.first()
        except Exception as e:
            # Log para debug
            import sys
            print(f"Error detecting current page: {e}", file=sys.stderr)
    
    # Obtener HomePage
    primary_menu = []
    secondary_menu = []
    
    try:
        from cms.models import HomePage
        home_page = HomePage.objects.filter(slug='madmusic-home').first()
        
        if home_page:
            # Generar menú primario (nivel 1) con sus hijos incluidos
            # Esto se usa tanto para hover como para detectar el item activo
            primary_menu = get_menu_items(home_page, current_page, max_depth=2, include_children=True)
            
            # Generar menú secundario (nivel 2) - solo para barra roja
            # Buscar qué item de nivel 1 está activo o es ancestro
            active_primary = None
            for item in primary_menu:
                if item.get('is_current') or item.get('is_ancestor'):
                    active_primary = item
                    break
            
            # Si hay un item activo/ancestro, usar sus hijos como menú secundario
            if active_primary and active_primary.get('children'):
                secondary_menu = active_primary['children']
    except Exception as e:
        # Log para debug
        import sys
        print(f"Error building menu: {e}", file=sys.stderr)
    
    return {
        'wagtail_menu_items': primary_menu,  # Mantener compatibilidad
        'wagtail_primary_menu': primary_menu,
        'wagtail_secondary_menu': secondary_menu,
    }

