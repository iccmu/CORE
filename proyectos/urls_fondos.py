from django.urls import include, path

urlpatterns = [
    path("", include("fondos_app.urls")),
]
