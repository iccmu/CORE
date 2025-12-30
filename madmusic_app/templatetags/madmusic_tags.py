"""
Template tags personalizados para madmusic_app
"""
from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def madmusic_url(slug):
    """
    Genera la URL para una página de madmusic usando el slug.
    Maneja correctamente slugs con barras.
    """
    try:
        return reverse('madmusic_pagina', kwargs={'slug': slug})
    except Exception:
        # Si falla, devolver URL directa
        return f'/madmusic/{slug}/'





