from django.db import models
from django import forms
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.images.models import Image
from wagtail import blocks

from .blocks import AccordionGroupBlock, ImageWithCaptionBlock, QuoteBlock


class ColorWidget(forms.TextInput):
    """Widget para seleccionar colores usando HTML5 color input"""
    input_type = 'color'


class HomePage(Page):
    """Página de inicio del sitio"""
    intro = RichTextField(blank=True, help_text="Texto de introducción")
    
    # Campos para el header/carrusel
    header_title = models.CharField(
        max_length=200, 
        blank=True, 
        default="MadMusic-CM H2019/HUM-5731",
        help_text="Título principal del header (carrusel)"
    )
    header_subtitle = models.CharField(
        max_length=300, 
        blank=True, 
        default="Espacios, géneros y públicos de la música en Madrid (ss. XVII-XX)",
        help_text="Subtítulo del header (carrusel)"
    )
    
    # Configuración de colores (opcional - si no se especifica, usa valores por defecto)
    primary_color = models.CharField(
        max_length=7,
        blank=True,
        default="",
        help_text="Color principal (deja vacío para usar #d11922)"
    )
    secondary_color = models.CharField(
        max_length=7,
        blank=True,
        default="",
        help_text="Color secundario (deja vacío para usar #c1272d)"
    )
    background_gradient_start = models.CharField(
        max_length=7,
        blank=True,
        default="",
        help_text="Gradiente header - inicio (deja vacío para usar #34495e)"
    )
    background_gradient_end = models.CharField(
        max_length=7,
        blank=True,
        default="",
        help_text="Gradiente header - fin (deja vacío para usar #2c3e50)"
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("header_title"),
        FieldPanel("header_subtitle"),
        MultiFieldPanel([
            FieldPanel("primary_color", widget=ColorWidget),
            FieldPanel("secondary_color", widget=ColorWidget),
            FieldPanel("background_gradient_start", widget=ColorWidget),
            FieldPanel("background_gradient_end", widget=ColorWidget),
        ], heading="Colores personalizados (opcional)"),
    ]

    subpage_types = ["cms.StandardPage", "cms.NewsIndexPage"]

    def get_featured_news(self):
        """Obtiene las 6 noticias destacadas desde NewsIndexPage"""
        news_index = NewsIndexPage.objects.child_of(self).live().first()
        if news_index:
            return list(NewsPage.objects.child_of(news_index).live().order_by("-date")[:6])
        return []
    
    def get_primary_color(self):
        """Retorna el color principal o el por defecto"""
        return self.primary_color or "#d11922"
    
    def get_secondary_color(self):
        """Retorna el color secundario o el por defecto"""
        return self.secondary_color or "#c1272d"
    
    def get_gradient_start(self):
        """Retorna el color de inicio del gradiente o el por defecto"""
        return self.background_gradient_start or "#34495e"
    
    def get_gradient_end(self):
        """Retorna el color final del gradiente o el por defecto"""
        return self.background_gradient_end or "#2c3e50"


class StandardPage(Page):
    """Página estándar con contenido enriquecido y bloques estructurados"""
    
    # Introducción en texto enriquecido simple
    intro = RichTextField(blank=True, help_text="Texto de introducción (opcional)")
    
    # Contenido principal usando StreamField para flexibilidad
    body = StreamField([
        ('paragraph', blocks.RichTextBlock(
            features=[
                'bold', 'italic',
                'link',
                'h2', 'h3', 'h4',
                'ol', 'ul',
                'blockquote',
                'hr',
            ],
            label='Párrafo',
            icon='doc-full'
        )),
        ('accordion_group', AccordionGroupBlock()),
        ('image', ImageWithCaptionBlock()),
        ('quote', QuoteBlock()),
        ('raw_html', blocks.RawHTMLBlock(
            help_text='HTML crudo - usar con precaución',
            icon='code'
        )),
    ], blank=True, use_json_field=True)
    
    # Color de acento para esta página (opcional)
    accent_color = models.CharField(
        max_length=7,
        blank=True,
        default="",
        help_text="Color de acento para títulos/enlaces (deja vacío para heredar de HomePage)"
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
        FieldPanel("accent_color", widget=ColorWidget, heading="Color de acento (opcional)"),
    ]

    parent_page_types = ["cms.HomePage"]
    
    def get_accent_color(self):
        """Retorna el color de acento o hereda del HomePage"""
        if self.accent_color:
            return self.accent_color
        # Heredar del HomePage padre
        home = self.get_ancestors().type(HomePage).last()
        if home:
            return home.specific.get_primary_color()
        return "#d11922"  # Por defecto


class NewsIndexPage(Page):
    """Página índice que lista las noticias"""
    intro = RichTextField(blank=True, help_text="Texto de introducción")

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    parent_page_types = ["cms.HomePage"]
    subpage_types = ["cms.NewsPage"]

    def get_context(self, request):
        context = super().get_context(request)
        news_pages = NewsPage.objects.child_of(self).live().order_by("-date")
        context["news_pages"] = news_pages
        return context


class NewsPage(Page):
    """Página de noticia individual"""
    date = models.DateField("Fecha de publicación")
    intro = models.CharField(max_length=250, blank=True, help_text="Introducción breve")
    body = RichTextField()
    featured_image = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Imagen destacada"
    )

    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("intro"),
        FieldPanel("body"),
        FieldPanel("featured_image"),
    ]

    parent_page_types = ["cms.NewsIndexPage"]

