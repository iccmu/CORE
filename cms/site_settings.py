"""
Configuraciones de sitio para colores y estilos.
Se editan desde el admin de Wagtail: Settings → Theme Settings
"""

from django.db import models
from django import forms
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.admin.panels import FieldPanel


class ColorWidget(forms.TextInput):
    """Widget para seleccionar colores usando HTML5 color input"""
    input_type = 'color'


@register_setting
class ThemeSettings(BaseSiteSetting):
    """
    Configuración de colores y estilos del sitio.
    Editable desde Wagtail Admin → Settings → Theme Settings
    """
    
    # Colores principales
    primary_color = models.CharField(
        max_length=7,
        default="#d11922",
        help_text="Color principal del sitio"
    )
    
    secondary_color = models.CharField(
        max_length=7,
        default="#c1272d",
        help_text="Color secundario"
    )
    
    background_gradient_start = models.CharField(
        max_length=7,
        default="#34495e",
        help_text="Color de inicio del gradiente del header"
    )
    
    background_gradient_end = models.CharField(
        max_length=7,
        default="#2c3e50",
        help_text="Color final del gradiente del header"
    )
    
    # Colores de texto
    text_primary = models.CharField(
        max_length=7,
        default="#333333",
        help_text="Color del texto principal"
    )
    
    text_light = models.CharField(
        max_length=7,
        default="#ffffff",
        help_text="Color del texto claro (sobre fondos oscuros)"
    )
    
    panels = [
        FieldPanel("primary_color", widget=ColorWidget),
        FieldPanel("secondary_color", widget=ColorWidget),
        FieldPanel("background_gradient_start", widget=ColorWidget),
        FieldPanel("background_gradient_end", widget=ColorWidget),
        FieldPanel("text_primary", widget=ColorWidget),
        FieldPanel("text_light", widget=ColorWidget),
    ]
    
    class Meta:
        verbose_name = "Theme Settings"
        verbose_name_plural = "Theme Settings"
