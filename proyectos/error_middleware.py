"""
Middleware para capturar errores 404 incluso en modo DEBUG
"""
from django.http import Http404
from django.shortcuts import render


class Custom404Middleware:
    """
    Middleware que captura errores 404 y muestra la página personalizada
    incluso cuando DEBUG=True
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        """
        Captura excepciones Http404 y renderiza el template personalizado
        """
        if isinstance(exception, Http404):
            return render(request, '404.html', status=404)
        return None

