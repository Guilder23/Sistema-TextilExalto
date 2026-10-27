from django.contrib import admin

from .models import DetalleEntrada, Entrada


class DetalleInline(admin.TabularInline):
    model = DetalleEntrada
    extra = 0


@admin.register(Entrada)
class EntradaAdmin(admin.ModelAdmin):
    inlines = [DetalleInline]
    list_display = ('id', 'fecha', 'proveedor', 'estado', 'usuario')
