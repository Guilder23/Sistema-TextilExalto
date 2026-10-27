from django.contrib import admin

from .models import DetalleSalida, Salida


class DetalleInline(admin.TabularInline):
    model = DetalleSalida
    extra = 0


@admin.register(Salida)
class SalidaAdmin(admin.ModelAdmin):
    inlines = [DetalleInline]
    list_display = ('id', 'fecha', 'cliente', 'total', 'estado', 'usuario')
