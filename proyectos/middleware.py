import logging

from django.conf import settings

logger = logging.getLogger(__name__)


class DomainUrlConfMiddleware:
    """
    Middleware que selecciona el URLConf apropiado basado en el dominio del host.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(":")[0]
        urlconf = settings.URLCONFS_BY_HOST.get(host, settings.ROOT_URLCONF)

        if urlconf != settings.ROOT_URLCONF:
            logger.debug(f"Usando URLConf '{urlconf}' para host '{host}'")

        request.urlconf = urlconf
        return self.get_response(request)







