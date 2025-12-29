from django.urls import path

from .views import madmusic_entrada, madmusic_home, madmusic_noticias, madmusic_pagina

urlpatterns = [
    # Landing del proyecto Madmusic usando Proyecto
    path("", madmusic_home, name="madmusic_home"),
    # Sección noticias tipo WordPress
    path("noticias/", madmusic_noticias, name="madmusic_noticias"),
    # Entradas individuales - deben ir antes de las páginas estáticas
    # Se sirven directamente en /madmusic/<slug>/ como en el sitio original
    path("<slug:slug>/", madmusic_entrada, name="madmusic_entrada"),
    # Páginas estáticas (debe ir al final para capturar todos los slugs con barras)
    path("<path:slug>/", madmusic_pagina, name="madmusic_pagina"),
]
