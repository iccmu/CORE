from django.http import JsonResponse
from django.shortcuts import render


def test_home(request):
    return render(
        request,
        "test/home.html",
        {
            "app_name": "Test",
            "host": request.get_host(),
        },
    )


def test_api(request):
    """Endpoint JSON para diagnóstico"""
    return JsonResponse(
        {
            "status": "ok",
            "message": "Test app funcionando correctamente",
            "host": request.get_host(),
        }
    )
