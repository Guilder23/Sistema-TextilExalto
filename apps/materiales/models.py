from django.db import models

from apps.categorias.models import Categoria


class Material(models.Model):
    UNIDADES = [
        ('unidad', 'Unidad'), ('metro', 'Metro'), ('kg', 'Kilogramo'),
        ('rollo', 'Rollo'), ('cono', 'Cono'), ('caja', 'Caja'),
    ]

    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='materiales')
    unidad = models.CharField(max_length=10, choices=UNIDADES, default='unidad')
    stock_actual = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    stock_minimo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = 'materiales'

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'

    @property
    def stock_bajo(self):
        return self.stock_actual <= self.stock_minimo
