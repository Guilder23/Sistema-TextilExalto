import os

from django.core.management.base import BaseCommand, CommandError

from apps.usuarios.models import Usuario


class Command(BaseCommand):
    help = 'Crea el usuario administrador inicial si todavía no existe.'

    def handle(self, *args, **options):
        username = os.getenv('ADMIN_USERNAME', 'admin').strip()
        password = os.getenv('ADMIN_PASSWORD', 'admin12345')

        if not username or not password:
            raise CommandError('ADMIN_USERNAME y ADMIN_PASSWORD no pueden estar vacíos.')

        usuario, creado = Usuario.objects.get_or_create(
            username=username,
            defaults={
                'rol': Usuario.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            },
        )

        if creado:
            usuario.set_password(password)
            usuario.save(update_fields=['password', 'rol', 'is_staff', 'is_superuser', 'is_active'])
            self.stdout.write(self.style.SUCCESS(f'Administrador "{username}" creado.'))
        else:
            self.stdout.write(f'El administrador "{username}" ya existe; no se modificó.')
