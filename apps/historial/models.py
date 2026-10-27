from django.conf import settings
from django.db import models


class Registro(models.Model):
    """Bitácora de actividad del sistema (solo lectura para el admin)."""

    ACCIONES = [
        ('login', 'Inicio de sesión'),
        ('login_fallido', 'Intento fallido'),
        ('logout', 'Cierre de sesión'),
        ('crear', 'Creación'),
        ('editar', 'Edición'),
        ('eliminar', 'Eliminación'),
        ('anular', 'Anulación'),
    ]
    MODULOS = [
        ('acceso', 'Acceso'),
        ('usuarios', 'Usuarios'),
        ('categorias', 'Categorías'),
        ('materiales', 'Materiales'),
        ('entradas', 'Entradas'),
        ('salidas', 'Salidas / Ventas'),
    ]

    fecha = models.DateTimeField(auto_now_add=True, db_index=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                on_delete=models.SET_NULL, related_name='registros')
    username = models.CharField(max_length=150, blank=True)
    modulo = models.CharField(max_length=20, choices=MODULOS)
    accion = models.CharField(max_length=15, choices=ACCIONES)
    descripcion = models.CharField(max_length=500)
    ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha', '-id']

    def __str__(self):
        return f'{self.fecha:%Y-%m-%d %H:%M:%S} {self.username} {self.accion}'
