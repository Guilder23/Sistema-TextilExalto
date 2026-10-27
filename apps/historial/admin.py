from django.contrib import admin

from .models import Registro


@admin.register(Registro)
class RegistroAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'username', 'modulo', 'accion', 'descripcion')
    list_filter = ('modulo', 'accion')
