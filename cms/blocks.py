"""
Bloques personalizados de Wagtail para el CMS.

Este módulo contiene bloques StreamField personalizados para
contenido estructurado como acordeones.
"""

from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class AccordionBlock(blocks.StructBlock):
    """
    Bloque para un acordeón individual (título + contenido colapsable).
    
    Usado dentro de AccordionGroupBlock para crear grupos de acordeones
    que pueden expandirse/colapsarse.
    """
    title = blocks.CharBlock(
        max_length=255,
        required=True,
        help_text="Título del acordeón (visible cuando está colapsado)"
    )
    
    content = blocks.RichTextBlock(
        required=True,
        features=[
            'bold', 'italic',
            'link',
            'h2', 'h3', 'h4',
            'ol', 'ul',
            'blockquote',
            'hr',
        ],
        help_text="Contenido del acordeón (HTML enriquecido)"
    )
    
    class Meta:
        icon = 'collapse-down'
        label = 'Acordeón'
        template = 'cms/blocks/accordion.html'


class AccordionGroupBlock(blocks.StructBlock):
    """
    Bloque para un grupo de acordeones.
    
    Permite crear múltiples acordeones que se comportan como un grupo
    (opcionalmente solo uno abierto a la vez).
    """
    heading = blocks.CharBlock(
        max_length=255,
        required=False,
        help_text="Título opcional para el grupo de acordeones"
    )
    
    accordions = blocks.ListBlock(
        AccordionBlock(),
        min_num=1,
        help_text="Lista de acordeones en este grupo"
    )
    
    # Configuración del comportamiento
    allow_multiple_open = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Permitir que múltiples acordeones estén abiertos al mismo tiempo"
    )
    
    first_accordion_open = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Abrir el primer acordeón por defecto"
    )
    
    class Meta:
        icon = 'list-ul'
        label = 'Grupo de Acordeones'
        template = 'cms/blocks/accordion_group.html'


class ImageWithCaptionBlock(blocks.StructBlock):
    """
    Bloque para una imagen con caption opcional.
    Útil para contenido dentro de acordeones.
    """
    image = ImageChooserBlock(required=True)
    caption = blocks.CharBlock(required=False, max_length=255)
    alt_text = blocks.CharBlock(
        required=False,
        max_length=255,
        help_text="Texto alternativo para accesibilidad"
    )
    
    class Meta:
        icon = 'image'
        label = 'Imagen con Caption'
        template = 'cms/blocks/image_with_caption.html'


class QuoteBlock(blocks.StructBlock):
    """
    Bloque para citas destacadas.
    Útil para contenido dentro de acordeones.
    """
    quote = blocks.TextBlock(required=True)
    attribution = blocks.CharBlock(required=False, max_length=255)
    
    class Meta:
        icon = 'openquote'
        label = 'Cita'
        template = 'cms/blocks/quote.html'
