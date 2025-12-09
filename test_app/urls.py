from django.urls import path
from .views import test_home, test_api

urlpatterns = [
    path("", test_home, name="test_home"),
    path("api/", test_api, name="test_api"),
]

