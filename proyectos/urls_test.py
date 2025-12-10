from django.urls import include, path

urlpatterns = [
    path("", include("test_app.urls")),
]
