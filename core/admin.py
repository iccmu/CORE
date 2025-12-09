from django.contrib import admin
from .models import Proyecto, Entrada, Pagina

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'slug', 'acronimo', 'fecha_inicio', 'fecha_fin']
    prepopulated_fields = {'slug': ('titulo',)}

@admin.register(Entrada)
class EntradaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'proyecto', 'fecha_publicacion']
    list_filter = ['proyecto', 'fecha_publicacion']
    prepopulated_fields = {'slug': ('titulo',)}

@admin.register(Pagina)
class PaginaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'slug', 'proyecto']
    prepopulated_fields = {'slug': ('titulo',)}
