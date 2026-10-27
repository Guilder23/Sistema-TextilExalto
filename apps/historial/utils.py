from .models import Registro


def ip_de(request):
    return request.META.get('REMOTE_ADDR') or None


def registrar(request, modulo, accion, descripcion, usuario=None):
    usuario = usuario or getattr(request, 'user', None)
    if usuario is not None and not getattr(usuario, 'is_authenticated', False):
        usuario = None
    Registro.objects.create(
        usuario=usuario,
        username=usuario.username if usuario else '',
        modulo=modulo, accion=accion,
        descripcion=descripcion[:500], ip=ip_de(request),
    )
