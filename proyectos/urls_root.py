from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from .views import index_view

urlpatterns = [
    path("", index_view, name="index"),
    path("fondos/", include("fondos_app.urls")),
    path("madmusic/", include("madmusic_app.urls")),
    path("test/", include("test_app.urls")),
]

# Servir archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
