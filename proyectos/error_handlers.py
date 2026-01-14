"""
Handlers personalizados para errores 404 y 500
"""
from django.shortcuts import render
from wagtail.models import Site


def handler404(request, exception=None):
    """
    Vista personalizada para errores 404
    Detecta el sitio actual (madmusic o madmusic3) y pasa contexto adecuado
    """
    # Valores por defecto
    site = None
    site_name = "ICCMU"
    home_url = "/"
    
    # Detectar basado en la ruta de la URL (más confiable que hostname)
    if '/madmusic3/' in request.path:
        # Estamos en madmusic3
        site = Site.objects.filter(root_page__slug='madmusic3-home').first()
        site_name = site.site_name if site else "Madmusic3"
        home_url = "/madmusic3/"
    elif '/madmusic/' in request.path:
        # Estamos en madmusic
        site = Site.objects.filter(root_page__slug='madmusic-home').first()
        site_name = site.site_name if site else "Madmusic"
        home_url = "/madmusic/"
    elif hasattr(request, 'site') and request.site:
        # Usar el sitio configurado por el middleware
        site = request.site
        site_name = site.site_name
        # Determinar home_url basado en el slug de la página raíz
        if site.root_page and site.root_page.slug == 'madmusic3-home':
            home_url = "/madmusic3/"
        elif site.root_page and site.root_page.slug == 'madmusic-home':
            home_url = "/madmusic/"
    else:
        # Detectar basado en el hostname
        hostname = request.get_host().split(':')[0]
        
        if 'madmusic3' in hostname:
            site = Site.objects.filter(root_page__slug='madmusic3-home').first()
            site_name = site.site_name if site else "Madmusic3"
            home_url = "/madmusic3/"
        else:
            # Default a madmusic
            site = Site.objects.filter(root_page__slug='madmusic-home').first()
            site_name = site.site_name if site else "Madmusic"
            home_url = "/madmusic/"
    
    context = {
        'site': site,
        'site_name': site_name,
        'home_url': home_url,
        'request': request,
    }
    
    return render(request, '404.html', context, status=404)


def handler500(request):
    """
    Vista personalizada para errores 500
    Detecta el sitio actual (madmusic o madmusic3) y pasa contexto adecuado
    """
    # Valores por defecto
    site = None
    site_name = "ICCMU"
    home_url = "/"
    
    try:
        # Detectar basado en la ruta de la URL (más confiable que hostname)
        if '/madmusic3/' in request.path:
            # Estamos en madmusic3
            site = Site.objects.filter(root_page__slug='madmusic3-home').first()
            site_name = site.site_name if site else "Madmusic3"
            home_url = "/madmusic3/"
        elif '/madmusic/' in request.path:
            # Estamos en madmusic
            site = Site.objects.filter(root_page__slug='madmusic-home').first()
            site_name = site.site_name if site else "Madmusic"
            home_url = "/madmusic/"
        elif hasattr(request, 'site') and request.site:
            # Usar el sitio configurado por el middleware
            site = request.site
            site_name = site.site_name
            # Determinar home_url basado en el slug de la página raíz
            if site.root_page and site.root_page.slug == 'madmusic3-home':
                home_url = "/madmusic3/"
            elif site.root_page and site.root_page.slug == 'madmusic-home':
                home_url = "/madmusic/"
        else:
            # Detectar basado en el hostname
            hostname = request.get_host().split(':')[0]
            
            if 'madmusic3' in hostname:
                site = Site.objects.filter(root_page__slug='madmusic3-home').first()
                site_name = site.site_name if site else "Madmusic3"
                home_url = "/madmusic3/"
            else:
                # Default a madmusic
                site = Site.objects.filter(root_page__slug='madmusic-home').first()
                site_name = site.site_name if site else "Madmusic"
                home_url = "/madmusic/"
    except Exception as e:
        # Si hay error obteniendo el sitio, usar valores por defecto
        # En errores 500, es mejor no fallar aquí
        pass
    
    context = {
        'site': site,
        'site_name': site_name,
        'home_url': home_url,
        'request': request,
    }
    
    return render(request, '500.html', context, status=500)

