from django.conf import settings
from django.db import models

from apps.materiales.models import Material


class Salida(models.Model):
    CONFIRMADA = 'confirmada'
    ANULADA = 'anulada'
    ESTADOS = [(CONFIRMADA, 'Confirmada'), (ANULADA, 'Anulada')]
    PAGOS = [
        ('efectivo', 'Efectivo'), ('transferencia', 'Transferencia'),
        ('tarjeta', 'Tarjeta'), ('qr', 'QR'), ('credito', 'Crédito'),
    ]

    fecha = models.DateField()
    cliente = models.CharField(max_length=150)
    documento_cliente = models.CharField('CI / NIT', max_length=30, blank=True)
    telefono_cliente = models.CharField(max_length=20, blank=True)
    metodo_pago = models.CharField(max_length=15, choices=PAGOS, default='efectivo')
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    observaciones = models.TextField(blank=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default=CONFIRMADA)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='salidas')
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha', '-id']

    @property
    def numero(self):
        return f'VEN-{self.pk:04d}'

    def __str__(self):
        return self.numero


class DetalleSalida(models.Model):
    salida = models.ForeignKey(Salida, on_delete=models.CASCADE, related_name='detalles')
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name='detalles_salida')
    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
