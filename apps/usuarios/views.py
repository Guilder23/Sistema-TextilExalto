from functools import wraps

from django.contrib import messages

from apps.historial.utils import registrar
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Usuario


def solo_admin(view):
    @wraps(view)
    @login_required
    def envoltura(request, *args, **kwargs):
        if not request.user.es_admin:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return envoltura


@login_required
def inicio(request):
    return render(request, 'base/inicio.html', {
        'total_usuarios': Usuario.objects.count(),
        'total_admins': Usuario.objects.filter(rol=Usuario.ADMIN).count(),
        'total_vendedores': Usuario.objects.filter(rol=Usuario.VENDEDOR).count(),
    })


@solo_admin
def lista(request):
    q = request.GET.get('q', '').strip()
    rol = request.GET.get('rol', '')
    usuarios = Usuario.objects.order_by('username')
    if q:
        usuarios = usuarios.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q)
            | Q(last_name__icontains=q) | Q(email__icontains=q)
        )
    if rol in (Usuario.ADMIN, Usuario.VENDEDOR):
        usuarios = usuarios.filter(rol=rol)
    return render(request, 'usuarios/lista.html', {
        'usuarios': usuarios, 'q': q, 'rol_filtro': rol, 'roles': Usuario.ROLES,
    })


def _validar(datos, usuario=None):
    errores = []
    username = datos.get('username', '').strip()
    password = datos.get('password', '')
    rol = datos.get('rol', '')
    if not username:
        errores.append('El nombre de usuario es obligatorio.')
    elif Usuario.objects.filter(username__iexact=username).exclude(pk=getattr(usuario, 'pk', None)).exists():
        errores.append('Ese nombre de usuario ya existe.')
    if rol not in (Usuario.ADMIN, Usuario.VENDEDOR):
        errores.append('Rol inválido.')
    if usuario is None or password:
        if not password:
            errores.append('La contraseña es obligatoria.')
        elif password != datos.get('password2', ''):
            errores.append('Las contraseñas no coinciden.')
        else:
            try:
                validate_password(password, usuario)
            except ValidationError as e:
                errores.extend(e.messages)
    return errores


def _asignar(usuario, datos):
    usuario.username = datos.get('username', '').strip()
    usuario.first_name = datos.get('first_name', '').strip()
    usuario.last_name = datos.get('last_name', '').strip()
    usuario.email = datos.get('email', '').strip()
    usuario.telefono = datos.get('telefono', '').strip()
    usuario.rol = datos.get('rol')
    usuario.is_active = datos.get('is_active') == 'on'
    if datos.get('password'):
        usuario.set_password(datos['password'])


@solo_admin
@require_POST
def crear(request):
    errores = _validar(request.POST)
    if errores:
        for e in errores:
            messages.error(request, e)
    else:
        usuario = Usuario()
        _asignar(usuario, request.POST)
        usuario.save()
        messages.success(request, f'Usuario "{usuario.username}" creado.')
        registrar(request, 'usuarios', 'crear', f'Creó el usuario "{usuario.username}" ({usuario.get_rol_display()}).')
    return redirect('usuarios:lista')


@solo_admin
@require_POST
def editar(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    errores = _validar(request.POST, usuario)
    if usuario == request.user and (request.POST.get('rol') != usuario.rol
                                    or request.POST.get('is_active') != 'on'):
        errores.append('No puedes cambiar tu propio rol ni desactivarte.')
    if errores:
        for e in errores:
            messages.error(request, e)
    else:
        _asignar(usuario, request.POST)
        usuario.save()
        messages.success(request, f'Usuario "{usuario.username}" actualizado.')
        registrar(request, 'usuarios', 'editar', f'Editó el usuario "{usuario.username}".')
    return redirect('usuarios:lista')


@solo_admin
@require_POST
def eliminar(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if usuario == request.user:
        messages.error(request, 'No puedes eliminar tu propia cuenta.')
    else:
        usuario.delete()
        messages.success(request, f'Usuario "{usuario.username}" eliminado.')
        registrar(request, 'usuarios', 'eliminar', f'Eliminó el usuario "{usuario.username}".')
    return redirect('usuarios:lista')
