from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from cms import views as cms_views

urlpatterns = [
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    
    # Backup download endpoints (staff-only)
    path("download-offline-backup/", cms_views.download_offline_backup, name="download_offline_backup"),
    path("download-offline/", cms_views.download_offline_backup_signed, name="download_offline_backup_signed"),
    path("generate-download-token/", cms_views.generate_download_token, name="generate_download_token"),
    path("download-from-azure/", cms_views.download_from_azure, name="download_from_azure"),
    path("list-backups/", cms_views.list_backups, name="list_backups"),
    
    # Wagtail pages (must be last)
    path("", include(wagtail_urls)),
]

# Handlers personalizados para errores
handler404 = 'proyectos.error_handlers.handler404'
handler500 = 'proyectos.error_handlers.handler500'

# Servir archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
