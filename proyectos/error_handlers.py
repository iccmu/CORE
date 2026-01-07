"""
Handlers personalizados para errores 404 y 500
"""
from django.shortcuts import render


def handler404(request, exception=None):
    """
    Vista personalizada para errores 404
    """
    return render(request, '404.html', status=404)


def handler500(request):
    """
    Vista personalizada para errores 500
    """
    return render(request, '500.html', status=500)

