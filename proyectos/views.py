from django.shortcuts import render


def index_view(request):
    """
    Vista que muestra un índice automático de todas las apps del proyecto disponibles.
    Solo muestra las apps personalizadas del proyecto, no las apps de Django.
    """
    # Lista explícita de apps del proyecto que queremos mostrar en el índice
    project_apps = [
        {
            "name": "fondos_app",
            "display_name": "Fondos",
            "slug": "fondos",
            "url": "/fondos/",
        },
        {
            "name": "madmusic_app",
            "display_name": "Madmusic",
            "slug": "madmusic",
            "url": "/madmusic/",
        },
        {
            "name": "test_app",
            "display_name": "Test",
            "slug": "test",
            "url": "/test/",
        },
    ]

    # Nota: 'core' no se incluye porque es una app de modelos compartidos,
    # no una app con interfaz propia

    context = {
        "apps": project_apps,
        "host": request.get_host(),
    }

    return render(request, "proyectos/index.html", context)
