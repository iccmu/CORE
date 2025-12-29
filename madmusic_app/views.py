from django.shortcuts import get_object_or_404, render

from core.models import Entrada, Pagina, Proyecto


def madmusic_home(request):
    proyecto = Proyecto.objects.filter(slug="madmusic").first()
    # Obtener últimas entradas destacadas para mostrar en la home
    entradas_destacadas = []
    if proyecto:
        entradas_destacadas = proyecto.entradas.all()[:6]  # Últimas 6 entradas
    return render(
        request, 
        "madmusic/home.html", 
        {
            "proyecto": proyecto, 
            "app_name": "Madmusic",
            "entradas_destacadas": entradas_destacadas
        }
    )


def madmusic_noticias(request):
    proyecto = get_object_or_404(Proyecto, slug="madmusic")
    entradas = proyecto.entradas.all()[:10]  # Últimas 10 noticias
    return render(
        request,
        "madmusic/noticias.html",
        {"entradas": entradas, "proyecto": proyecto, "app_name": "Madmusic"},
    )


def madmusic_entrada(request, slug):
    # Primero intentar buscar como Entrada
    entrada = Entrada.objects.filter(slug=slug).first()
    if entrada:
        return render(
            request,
            "madmusic/entrada.html",
            {"entrada": entrada, "proyecto": entrada.proyecto, "app_name": "Madmusic"},
        )
    
    # Si no es una Entrada, verificar si es una Pagina y redirigir
    pagina = Pagina.objects.filter(slug=slug).first()
    if pagina:
        return madmusic_pagina(request, slug)
    
    # Si no existe ni como Entrada ni como Pagina, lanzar 404
    from django.http import Http404
    raise Http404(f"No se encontró ninguna Entrada o Página con el slug: {slug}")


def build_sidebar_menu(proyecto, current_slug=None):
    """Construir el menú del sidebar basado en las páginas del proyecto"""
    if not proyecto:
        return []
    
    # Obtener todas las páginas del proyecto ordenadas por slug
    paginas = Pagina.objects.filter(proyecto=proyecto).order_by('slug')
    
    # Páginas que NO deben aparecer en el sidebar (están en el menú principal)
    excluded_pages = [
        'noticias',
        'contacto',
        'cursos-de-verano',  # Puede estar duplicado o ser independiente
    ]
    
    # Estructura del menú basada en el sitio original (páginas principales)
    main_pages = [
        'proyecto-madmusic',
        'equipo',
        'divulgacion-cientifica',
        'servicios-e-infraestructura',
        'transferencia',
        'formacion-empleo'
    ]
    
    menu_items = []
    processed_slugs = set()  # Para evitar duplicados
    
    # Construir el menú basado en las páginas principales
    for parent_slug in main_pages:
        parent_pagina = paginas.filter(slug=parent_slug).first()
        if not parent_pagina:
            continue
        
        processed_slugs.add(parent_slug)
        
        # Buscar hijos automáticamente (páginas cuyo slug empiece con parent_slug/)
        children = []
        for pagina in paginas:
            # Evitar duplicados y páginas excluidas
            if pagina.slug in processed_slugs:
                continue
            if any(excluded in pagina.slug for excluded in excluded_pages):
                continue
            
            if pagina.slug.startswith(parent_slug + '/') and pagina.slug != parent_slug:
                # Verificar que no sea un nieto (tiene más de un nivel de profundidad)
                relative_slug = pagina.slug[len(parent_slug)+1:]
                if '/' not in relative_slug:  # Solo hijos directos
                    children.append({
                        'pagina': pagina,
                        'slug': pagina.slug,
                        'titulo': pagina.titulo,
                        'is_current': current_slug == pagina.slug
                    })
                    processed_slugs.add(pagina.slug)
        
        # Ordenar hijos por slug
        children.sort(key=lambda x: x['slug'])
        
        # Determinar si el item actual está activo
        is_current = current_slug == parent_slug
        is_ancestor = current_slug and current_slug.startswith(parent_slug + '/')
        
        # Corregir títulos si es necesario
        titulo = parent_pagina.titulo
        if parent_slug == 'formacion-empleo' and titulo == 'Empleo':
            titulo = 'Formación | Empleo'
        
        menu_items.append({
            'pagina': parent_pagina,
            'slug': parent_pagina.slug,
            'titulo': titulo,
            'children': children,
            'is_current': is_current,
            'is_ancestor': is_ancestor,
            'has_children': len(children) > 0
        })
    
    return menu_items


def madmusic_pagina(request, slug):
    # Limpiar slug (eliminar barras al inicio/final)
    slug = slug.strip('/')
    
    # IMPORTANTE: Primero verificar si existe una entrada con este slug
    # Las entradas tienen prioridad sobre las páginas estáticas
    entrada = Entrada.objects.filter(slug=slug).first()
    if entrada:
        # Si existe una entrada, redirigir a la vista de entrada
        return madmusic_entrada(request, slug)
    
    # Buscar página por slug exacto
    pagina = Pagina.objects.filter(slug=slug).first()
    
    if not pagina:
        # Intentar buscar por slug sin barras iniciales/finales
        slug_clean = slug.rstrip('/').lstrip('/')
        pagina = Pagina.objects.filter(slug=slug_clean).first()
    
    if not pagina:
        # Si no existe la página, intentar mostrar contenido del proyecto
        proyecto = Proyecto.objects.filter(slug=slug).first()
        if proyecto:
            sidebar_menu = build_sidebar_menu(proyecto, slug)
            return render(
                request,
                "madmusic/proyecto.html",
                {
                    "proyecto": proyecto, 
                    "app_name": "Madmusic",
                    "sidebar_menu": sidebar_menu
                },
            )
        # 404 si no existe nada
        from django.http import Http404
        raise Http404(f"Página no encontrada: {slug}")
    
    # Construir el menú del sidebar
    sidebar_menu = build_sidebar_menu(pagina.proyecto, slug)
    
    return render(
        request,
        "madmusic/pagina.html",
        {
            "pagina": pagina, 
            "proyecto": pagina.proyecto, 
            "app_name": "Madmusic",
            "sidebar_menu": sidebar_menu
        },
    )
