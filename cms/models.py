from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.images.models import Image
from wagtail import blocks

from .blocks import AccordionGroupBlock, ImageWithCaptionBlock, QuoteBlock


class HomePage(Page):
    """Página de inicio del sitio"""
    intro = RichTextField(blank=True, help_text="Texto de introducción")

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["cms.StandardPage", "cms.NewsIndexPage"]

    def get_featured_news(self):
        """Obtiene las 6 noticias destacadas desde NewsIndexPage"""
        news_index = NewsIndexPage.objects.child_of(self).live().first()
        if news_index:
            return list(NewsPage.objects.child_of(news_index).live().order_by("-date")[:6])
        return []


class StandardPage(Page):
    """Página estándar con contenido enriquecido y bloques estructurados"""
    
    # Introducción en texto enriquecido simple
    intro = RichTextField(blank=True, help_text="Texto de introducción (opcional)")
    
    # Contenido principal usando StreamField para flexibilidad
    body = StreamField([
        ('paragraph', blocks.RichTextBlock(
            features=[
                'h2', 'h3', 'h4', 'h5', 'h6',
                'bold', 'italic',
                'ol', 'ul',
                'link', 'document-link',
                'image', 'embed',
                'hr',
                'blockquote',
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

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    parent_page_types = ["cms.HomePage"]


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

