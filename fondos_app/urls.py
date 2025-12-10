from django.urls import path

from .views import fondos_home

urlpatterns = [
    path("", fondos_home, name="fondos_home"),
]


