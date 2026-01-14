from django.apps import AppConfig


class CmsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cms"
    
    def ready(self):
        # Importar site_settings para registrar los modelos
        import cms.site_settings  # noqa



