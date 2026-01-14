"""
Comando para crear un usuario con acceso solo a madmusic3.

Uso:
    python manage.py create_madmusic3_user
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from wagtail.models import GroupPagePermission
from cms.models import HomePage


class Command(BaseCommand):
    help = "Crea un usuario con acceso solo a madmusic3"

    def handle(self, *args, **options):
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("CREANDO USUARIO MADMUSIC3")
        self.stdout.write("=" * 80 + "\n")

        # 1. Crear o actualizar usuario
        email = "malvarez@iccmu.es"
        username = "malvarez"
        password = "12345678"
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,  # Necesario para acceder al admin
                "is_superuser": False,  # NO es superusuario
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f"✓ Usuario creado: {username}")
            )
        else:
            self.stdout.write(f"✓ Usuario existente: {username}")

        # 2. Crear o obtener grupo "Madmusic3 Editors"
        group, created = Group.objects.get_or_create(
            name="Madmusic3 Editors"
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS("✓ Grupo 'Madmusic3 Editors' creado")
            )
        else:
            self.stdout.write("✓ Grupo 'Madmusic3 Editors' existente")

        # 3. Agregar usuario al grupo
        user.groups.add(group)
        self.stdout.write(f"✓ Usuario '{username}' agregado al grupo")

        # 4. Buscar la HomePage de madmusic3
        madmusic3_home = HomePage.objects.filter(slug="madmusic3-home").first()
        
        if not madmusic3_home:
            self.stdout.write(
                self.style.ERROR("⚠ No se encontró la HomePage de madmusic3")
            )
            return

        # 5. Configurar permisos del grupo sobre madmusic3
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        
        # Limpiar permisos anteriores del grupo
        GroupPagePermission.objects.filter(group=group).delete()
        
        # Obtener el ContentType de Page
        page_content_type = ContentType.objects.get_for_model(madmusic3_home)
        
        # Crear permisos para la HomePage de madmusic3 y sus descendientes
        permission_codenames = [
            'add_page',      # Crear páginas
            'change_page',   # Editar páginas
            'publish_page',  # Publicar páginas
            'lock_page',     # Bloquear páginas
        ]
        
        for codename in permission_codenames:
            try:
                permission = Permission.objects.get(
                    content_type__app_label='wagtailcore',
                    codename=codename
                )
                GroupPagePermission.objects.create(
                    group=group,
                    page=madmusic3_home,
                    permission=permission,
                )
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠ Permiso '{codename}' no encontrado")
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Permisos configurados para '{group.name}' en '{madmusic3_home.title}'"
            )
        )

        # 6. Resumen
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(
            self.style.SUCCESS("✓ Usuario configurado exitosamente!")
        )
        self.stdout.write("\nCredenciales:")
        self.stdout.write(f"  - Usuario: {username}")
        self.stdout.write(f"  - Email: {email}")
        self.stdout.write(f"  - Contraseña: {password}")
        self.stdout.write(f"\nPermisos:")
        self.stdout.write(f"  - Puede editar SOLO páginas bajo '{madmusic3_home.title}'")
        self.stdout.write(f"  - NO puede editar madmusic ni otras secciones")
        self.stdout.write(f"  - NO es superusuario")
        self.stdout.write("\nAcceso:")
        self.stdout.write("  - Admin: http://127.0.0.1:8000/admin/")
        self.stdout.write("=" * 80 + "\n")
