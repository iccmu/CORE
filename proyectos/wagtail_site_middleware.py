"""
Middleware para configurar el Site de Wagtail correcto según el path y hostname.

Este middleware detecta prefijos de ruta específicos (como /madmusic/ o /madmusic3/)
y configura el Site de Wagtail correspondiente, usando el hostname de la request
cuando sea posible (para mantener localhost en desarrollo).
"""

from wagtail.models import Site


class WagtailSiteMiddleware:
    """
    Middleware que configura el Site de Wagtail según el prefijo de la URL.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]
        port_str = request.get_host().split(':')[1] if ':' in request.get_host() else '80'
        port = int(port_str) if port_str != '' else 80
        
        # Mapeo de prefijos de path según el hostname
        # Si estamos en localhost/127.0.0.1, usar Sites locales
        # Si estamos en dominios de producción, usar Sites de producción
        if host in ['localhost', '127.0.0.1']:
            path_to_site_lookup = {
                '/madmusic3/': ('localhost', 8000),  # Usar Site local para madmusic3
                '/madmusic/': ('127.0.0.1', 8000),   # Usar Site local para madmusic
            }
        else:
            # En producción, usar los dominios reales (ya manejado por DomainUrlConfMiddleware)
            path_to_site_lookup = {}
        
        # Detectar el prefijo de path y configurar el Site correspondiente
        for path_prefix, (site_hostname, site_port) in path_to_site_lookup.items():
            if request.path.startswith(path_prefix):
                # Buscar el Site correspondiente
                site = Site.objects.filter(hostname=site_hostname, port=site_port).first()
                if site:
                    # Configurar el Site en el request para que Wagtail lo use
                    request._wagtail_site = site
                break

        response = self.get_response(request)
        return response
