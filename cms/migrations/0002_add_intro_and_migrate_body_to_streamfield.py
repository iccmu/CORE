# Generated manually to handle data migration from RichTextField to StreamField

import wagtail.fields
from django.db import migrations
import json


def convert_richtext_to_streamfield(apps, schema_editor):
    """
    Convierte el contenido existente de RichTextField a formato StreamField.
    Envuelve el contenido HTML existente en un bloque 'raw_html'.
    """
    StandardPage = apps.get_model('cms', 'StandardPage')
    
    for page in StandardPage.objects.all():
        if page.body_old:
            # Convertir el contenido RichText a un bloque raw_html en StreamField
            stream_data = [{
                'type': 'raw_html',
                'value': str(page.body_old)
            }]
            page.body = json.dumps(stream_data)
            page.save(update_fields=['body'])


def reverse_migration(apps, schema_editor):
    """
    Revertir: copiar el primer bloque raw_html de vuelta a body_old.
    """
    StandardPage = apps.get_model('cms', 'StandardPage')
    
    for page in StandardPage.objects.all():
        if page.body:
            try:
                stream_data = json.loads(page.body)
                if stream_data and len(stream_data) > 0:
                    first_block = stream_data[0]
                    if first_block.get('type') == 'raw_html':
                        page.body_old = first_block.get('value', '')
                        page.save(update_fields=['body_old'])
            except json.JSONDecodeError:
                pass


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0001_initial"),
    ]

    operations = [
        # Paso 1: Añadir el campo intro
        migrations.AddField(
            model_name="standardpage",
            name="intro",
            field=wagtail.fields.RichTextField(
                blank=True, help_text="Texto de introducción (opcional)"
            ),
        ),
        
        # Paso 2: Renombrar body a body_old
        migrations.RenameField(
            model_name="standardpage",
            old_name="body",
            new_name="body_old",
        ),
        
        # Paso 3: Crear nuevo campo body como StreamField
        migrations.AddField(
            model_name="standardpage",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    ("paragraph", 0),
                    ("accordion_group", 8),
                    ("image", 12),
                    ("quote", 14),
                    ("raw_html", 15),
                ],
                blank=True,
                block_lookup={
                    0: (
                        "wagtail.blocks.RichTextBlock",
                        (),
                        {
                            "features": [
                                "h2",
                                "h3",
                                "h4",
                                "h5",
                                "h6",
                                "bold",
                                "italic",
                                "ol",
                                "ul",
                                "link",
                                "document-link",
                                "image",
                                "embed",
                                "hr",
                                "blockquote",
                            ],
                            "icon": "doc-full",
                            "label": "Párrafo",
                        },
                    ),
                    1: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": "Título opcional para el grupo de acordeones",
                            "max_length": 255,
                            "required": False,
                        },
                    ),
                    2: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": "Título del acordeón (visible cuando está colapsado)",
                            "max_length": 255,
                            "required": True,
                        },
                    ),
                    3: (
                        "wagtail.blocks.RichTextBlock",
                        (),
                        {
                            "features": [
                                "h2",
                                "h3",
                                "h4",
                                "h5",
                                "h6",
                                "bold",
                                "italic",
                                "ol",
                                "ul",
                                "link",
                                "document-link",
                                "image",
                                "embed",
                                "hr",
                                "blockquote",
                                "superscript",
                                "subscript",
                                "strikethrough",
                                "code",
                            ],
                            "help_text": "Contenido del acordeón (HTML enriquecido)",
                            "required": True,
                        },
                    ),
                    4: (
                        "wagtail.blocks.StructBlock",
                        [[("title", 2), ("content", 3)]],
                        {},
                    ),
                    5: (
                        "wagtail.blocks.ListBlock",
                        (4,),
                        {
                            "help_text": "Lista de acordeones en este grupo",
                            "min_num": 1,
                        },
                    ),
                    6: (
                        "wagtail.blocks.BooleanBlock",
                        (),
                        {
                            "default": False,
                            "help_text": "Permitir que múltiples acordeones estén abiertos al mismo tiempo",
                            "required": False,
                        },
                    ),
                    7: (
                        "wagtail.blocks.BooleanBlock",
                        (),
                        {
                            "default": False,
                            "help_text": "Abrir el primer acordeón por defecto",
                            "required": False,
                        },
                    ),
                    8: (
                        "wagtail.blocks.StructBlock",
                        [
                            [
                                ("heading", 1),
                                ("accordions", 5),
                                ("allow_multiple_open", 6),
                                ("first_accordion_open", 7),
                            ]
                        ],
                        {},
                    ),
                    9: (
                        "wagtail.images.blocks.ImageChooserBlock",
                        (),
                        {"required": True},
                    ),
                    10: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"max_length": 255, "required": False},
                    ),
                    11: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": "Texto alternativo para accesibilidad",
                            "max_length": 255,
                            "required": False,
                        },
                    ),
                    12: (
                        "wagtail.blocks.StructBlock",
                        [[("image", 9), ("caption", 10), ("alt_text", 11)]],
                        {},
                    ),
                    13: ("wagtail.blocks.TextBlock", (), {"required": True}),
                    14: (
                        "wagtail.blocks.StructBlock",
                        [[("quote", 13), ("attribution", 10)]],
                        {},
                    ),
                    15: (
                        "wagtail.blocks.RawHTMLBlock",
                        (),
                        {
                            "help_text": "HTML crudo - usar con precaución",
                            "icon": "code",
                        },
                    ),
                },
            ),
        ),
        
        # Paso 4: Migrar datos de body_old a body
        migrations.RunPython(
            convert_richtext_to_streamfield,
            reverse_migration
        ),
        
        # Paso 5: Eliminar el campo body_old
        migrations.RemoveField(
            model_name="standardpage",
            name="body_old",
        ),
    ]
