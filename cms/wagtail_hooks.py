"""
Hooks de Wagtail para personalización del admin y userbar.
"""
from django.templatetags.static import static
from django.urls import reverse
from django.http import HttpResponseRedirect
from wagtail import hooks


@hooks.register("register_admin_branding")
def admin_branding():
    """Personalizar el branding del admin de Wagtail."""
    return {
        "logo": static("madmusic/img/logo_wagtail.png"),
        "logo_small": static("madmusic/img/logo_wagtail.png"),
        "site_name": "ICCMU CMS",
        "site_url": "/madmusic/",
    }


@hooks.register('insert_global_admin_css')
def global_admin_css():
    """Añadir CSS personalizado al admin de Wagtail para ajustar el logo circular."""
    from django.templatetags.static import static
    logo_url = static('madmusic/img/logo_wagtail.png')
    
    return f"""
    <style>
        /* Logo circular en el admin */
        .sidebar-wagtail-branding__logo {{
            max-width: 60px !important;
            max-height: 60px !important;
            border-radius: 50% !important;
            object-fit: contain !important;
        }}
        
        /* Userbar - Reemplazar el icono de Wagtail con nuestro logo */
        .wagtail-userbar-trigger {{
            background-image: url('{logo_url}') !important;
            background-size: 90% !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            border-radius: 50% !important;
            transition: all 0.3s ease !important;
        }}
        
        /* Ocultar el SVG original de Wagtail en el userbar */
        .wagtail-userbar-trigger svg {{
            display: none !important;
        }}
        
        /* Hover effect en el userbar */
        .wagtail-userbar-trigger:hover {{
            transform: scale(1.1) rotate(5deg) !important;
            box-shadow: 0 4px 12px rgba(209, 25, 34, 0.5) !important;
        }}
        
        /* Logo en items del userbar */
        .wagtail-userbar__logo img {{
            border-radius: 50% !important;
            object-fit: contain !important;
        }}
    </style>
    """


@hooks.register('after_edit_page')
def redirect_to_edit_page(request, page):
    """
    Después de editar/publicar una página, mantener al usuario en la página de edición
    en lugar de redirigirlo a la vista de exploración (explore view).
    """
    # Solo aplicar esta redirección si el usuario NO es superusuario
    # Los superusuarios pueden preferir el comportamiento por defecto
    if not request.user.is_superuser:
        # Redirigir de vuelta a la página de edición
        edit_url = reverse('wagtailadmin_pages:edit', args=[page.id])
        return HttpResponseRedirect(edit_url)
