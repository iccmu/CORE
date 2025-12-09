from django.urls import path
from .views import madmusic_home

urlpatterns = [
    path("", madmusic_home, name="madmusic_home"),
]

