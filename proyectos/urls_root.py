from django.urls import path, include
from .views import index_view

urlpatterns = [
    path("", index_view, name="index"),
    path("fondos/", include("fondos_app.urls")),
    path("madmusic/", include("madmusic_app.urls")),
    path("test/", include("test_app.urls")),
]

