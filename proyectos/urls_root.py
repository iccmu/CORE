from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from .views import index_view

urlpatterns = [
    path("", index_view, name="index"),
    # Admin de Wagtail (accesible desde localhost)
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("fondos/", include("fondos_app.urls")),
    # Madmusic ahora usa Wagtail CMS
    path("madmusic/admin/", include(wagtailadmin_urls)),
    path("madmusic/documents/", include(wagtaildocs_urls)),
    path("madmusic/", include(wagtail_urls)),
    path("test/", include("test_app.urls")),
]

# Handlers personalizados para errores
handler404 = 'proyectos.error_handlers.handler404'
handler500 = 'proyectos.error_handlers.handler500'

# Servir archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
