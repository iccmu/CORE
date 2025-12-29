"""
Management command rápido para crear todas las páginas básicas de Madmusic
"""
from django.core.management.base import BaseCommand

from core.models import Entrada, Pagina, Proyecto


class Command(BaseCommand):
    help = "Crea rápidamente todas las páginas básicas de Madmusic para que los enlaces funcionen"

    def handle(self, *args, **options):
        # Crear o obtener proyecto Madmusic
        proyecto, created = Proyecto.objects.get_or_create(
            slug="madmusic",
            defaults={
                "titulo": "MadMusic-CM",
                "acronimo": "MADMUSIC",
                "resumen": "Espacios, géneros y públicos de la música en Madrid (ss. XVII-XX)",
                "cuerpo": "El proyecto MadMusic propone investigar, publicar e interpretar obras del patrimonio musical madrileño de los siglos XVII-XX olvidadas por estudiosos y gestores, proporcionando obras de calidad a programadores culturales para conocimiento del público.",
                "fecha_inicio": "2020-01-01",
                "url_oficial": "https://madmusic.iccmu.es/",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"✓ Proyecto creado: {proyecto.titulo}"))
        else:
            self.stdout.write(f"  Proyecto existente: {proyecto.titulo}")

        # Definir todas las páginas del menú con contenido básico
        paginas_menu = {
            # Acerca de MadMusic
            "proyecto-madmusic": {
                "titulo": "Acerca de MadMusic",
                "cuerpo": "MadMusic-CM es un proyecto de investigación que estudia los espacios, géneros y públicos de la música en Madrid desde el siglo XVII hasta el XX.",
            },
            "proyecto-madmusic/objetivos": {
                "titulo": "Objetivos",
                "cuerpo": "Los objetivos del proyecto MadMusic incluyen la investigación, publicación e interpretación de obras del patrimonio musical madrileño.",
            },
            "proyecto-madmusic/investigacion": {
                "titulo": "Líneas de investigación",
                "cuerpo": "El proyecto desarrolla diversas líneas de investigación sobre la música en Madrid a lo largo de los siglos.",
            },
            # Equipo
            "equipo": {
                "titulo": "Equipo",
                "cuerpo": "El equipo del proyecto MadMusic está formado por más de cuarenta investigadores españoles y extranjeros de reconocimiento internacional.",
            },
            "equipo/alvaro-torrente": {
                "titulo": "Álvaro Torrente – Coordinador",
                "cuerpo": "Álvaro Torrente es el coordinador del proyecto MadMusic.",
            },
            "equipo/grupos-beneficiarios": {
                "titulo": "Grupos Beneficiarios",
                "cuerpo": "Información sobre los grupos beneficiarios del proyecto.",
            },
            "equipo/grupos-asociados": {
                "titulo": "Grupos Asociados",
                "cuerpo": "Información sobre los grupos asociados al proyecto.",
            },
            "equipo/participantes": {
                "titulo": "Participantes MadMusic 1",
                "cuerpo": "Lista de participantes de la primera edición del proyecto MadMusic.",
            },
            # Resultados científicos
            "divulgacion-cientifica": {
                "titulo": "Resultados científicos",
                "cuerpo": "Resultados y publicaciones científicas del proyecto MadMusic.",
            },
            "divulgacion-cientifica/archivos": {
                "titulo": "Fondos documentales",
                "cuerpo": "Fondos documentales relacionados con el proyecto.",
            },
            "divulgacion-cientifica/cuadernos-de-musica-iberoamericana": {
                "titulo": "Cuadernos de Música Iberoamericana",
                "cuerpo": "Publicación de cuadernos de música iberoamericana.",
            },
            "divulgacion-cientifica/articulos-en-revistas-cientificas": {
                "titulo": "Publicaciones",
                "cuerpo": "Artículos publicados en revistas científicas.",
            },
            "divulgacion-cientifica/publicaciones-en-abierto": {
                "titulo": "Publicaciones en abierto",
                "cuerpo": "Publicaciones disponibles en acceso abierto.",
            },
            "divulgacion-cientifica/congresos-madmusic": {
                "titulo": "Congresos | Seminarios",
                "cuerpo": "Congresos y seminarios organizados por el proyecto.",
            },
            "divulgacion-cientifica/publicaciones-madmusic-2": {
                "titulo": "Destacados MadMusic 1",
                "cuerpo": "Publicaciones destacadas de la primera edición del proyecto.",
            },
            # Servicios
            "servicios-e-infraestructura": {
                "titulo": "Servicios e Infraestructura",
                "cuerpo": "Servicios e infraestructura disponibles en el ICCMU.",
            },
            # Transferencia
            "transferencia": {
                "titulo": "Entidades y Transferencia",
                "cuerpo": "Información sobre entidades colaboradoras y transferencia de conocimiento.",
            },
            "transferencia/empresas": {
                "titulo": "Entidades colaboradoras",
                "cuerpo": "Lista de entidades colaboradoras del proyecto.",
            },
            "transferencia/conferencias": {
                "titulo": "Conferencias",
                "cuerpo": "Conferencias organizadas y participadas por el proyecto.",
            },
            "transferencia/conciertos": {
                "titulo": "Conciertos | Grabaciones",
                "cuerpo": "Conciertos y grabaciones realizadas en el marco del proyecto.",
            },
            "transferencia/exposiciones": {
                "titulo": "Exposiciones | Eventos",
                "cuerpo": "Exposiciones y eventos relacionados con el proyecto.",
            },
            "transferencia/divulgacion": {
                "titulo": "Divulgación",
                "cuerpo": "Actividades de divulgación científica del proyecto.",
            },
            # Formación
            "formacion-empleo": {
                "titulo": "Formación | Empleo",
                "cuerpo": "Ofertas de formación y empleo relacionadas con el proyecto.",
            },
            "formacion-empleo/formacion": {
                "titulo": "Tesis doctorales y TFMs",
                "cuerpo": "Información sobre tesis doctorales y trabajos de fin de máster.",
            },
            "cursos-de-verano": {
                "titulo": "Cursos de verano",
                "cuerpo": "Cursos de verano organizados por el ICCMU.",
            },
            "formacion-empleo/empleo": {
                "titulo": "Empleo",
                "cuerpo": "Ofertas de empleo relacionadas con el proyecto.",
            },
            # Otros
            "contacto": {
                "titulo": "Contacto",
                "cuerpo": "Información de contacto del Instituto Complutense de Ciencias Musicales.",
            },
        }

        pages_created = 0
        pages_existing = 0

        self.stdout.write("\nCreando páginas del menú...")
        for slug, datos in paginas_menu.items():
            pagina, created = Pagina.objects.get_or_create(
                slug=slug,
                defaults={
                    "proyecto": proyecto,
                    "titulo": datos["titulo"],
                    "cuerpo": datos["cuerpo"],
                },
            )
            if created:
                pages_created += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓ {slug}"))
            else:
                pages_existing += 1

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("COMPLETADO"))
        self.stdout.write(f"  Páginas creadas: {pages_created}")
        self.stdout.write(f"  Páginas existentes: {pages_existing}")
        self.stdout.write("=" * 80)
        self.stdout.write("\nTodos los enlaces del menú ahora deberían funcionar!")




