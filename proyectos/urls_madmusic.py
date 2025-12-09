from django.urls import path, include

urlpatterns = [
    path("", include("madmusic_app.urls")),
]

