from django.urls import path, include

urlpatterns = [
    path("", include("fondos_app.urls")),
]

