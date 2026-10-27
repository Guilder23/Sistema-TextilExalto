from django.conf import settings
from django.db import models

from apps.materiales.models import Material


class Entrada(models.Model):
    CONFIRMADA = 'confirmada'
    ANULADA = 'anulada'
    ESTADOS = [(CONFIRMADA, 'Confirmada'), (ANULADA, 'Anulada')]

    fecha = models.DateField()
    proveedor = models.CharField(max_length=150)
    documento = models.CharField(max_length=60, blank=True)
    observaciones = models.TextField(blank=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default=CONFIRMADA)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='entradas')
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha', '-id']

    @property
    def numero(self):
        return f'ENT-{self.pk:04d}'

    def __str__(self):
        return self.numero


class DetalleEntrada(models.Model):
    entrada = models.ForeignKey(Entrada, on_delete=models.CASCADE, related_name='detalles')
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name='detalles_entrada')
    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def subtotal(self):
        return self.cantidad * self.costo_unitario
