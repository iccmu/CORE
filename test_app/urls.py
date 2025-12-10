from django.urls import path

from .views import test_api, test_home

urlpatterns = [
    path("", test_home, name="test_home"),
    path("api/", test_api, name="test_api"),
]
