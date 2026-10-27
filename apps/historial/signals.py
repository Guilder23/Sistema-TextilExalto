from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from .models import Registro
from .utils import registrar


@receiver(user_logged_in)
def al_iniciar_sesion(sender, request, user, **kwargs):
    registrar(request, 'acceso', 'login', 'Inició sesión.', usuario=user)


@receiver(user_logged_out)
def al_cerrar_sesion(sender, request, user, **kwargs):
    if user is not None:
        registrar(request, 'acceso', 'logout', 'Cerró sesión.', usuario=user)


@receiver(user_login_failed)
def al_fallar_login(sender, credentials, request=None, **kwargs):
    Registro.objects.create(
        username=str(credentials.get('username', ''))[:150], modulo='acceso', accion='login_fallido',
        descripcion='Intento de inicio de sesión fallido.',
        ip=request.META.get('REMOTE_ADDR') if request is not None else None,
    )
