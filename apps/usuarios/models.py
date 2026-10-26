from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    ADMIN = 'admin'
    VENDEDOR = 'vendedor'
    ROLES = [(ADMIN, 'Administrador'), (VENDEDOR, 'Vendedor')]

    rol = models.CharField(max_length=10, choices=ROLES, default=VENDEDOR)
    telefono = models.CharField(max_length=20, blank=True)

    @property
    def es_admin(self):
        return self.rol == self.ADMIN

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.rol = self.ADMIN
        super().save(*args, **kwargs)
