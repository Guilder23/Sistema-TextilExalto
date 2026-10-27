from django.contrib import messages

from apps.historial.utils import registrar
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.usuarios.views import solo_admin

from .models import Categoria


@login_required
def lista(request):
    q = request.GET.get('q', '').strip()
    categorias = Categoria.objects.annotate(total_materiales=Count('materiales'))
    if q:
        categorias = categorias.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    return render(request, 'categorias/lista.html', {'categorias': categorias, 'q': q})


def _validar(datos, categoria=None):
    nombre = datos.get('nombre', '').strip()
    if not nombre:
        return ['El nombre es obligatorio.']
    if Categoria.objects.filter(nombre__iexact=nombre).exclude(pk=getattr(categoria, 'pk', None)).exists():
        return ['Ya existe una categoría con ese nombre.']
    return []


def _asignar(categoria, datos):
    categoria.nombre = datos.get('nombre', '').strip()
    categoria.descripcion = datos.get('descripcion', '').strip()
    categoria.activa = datos.get('activa') == 'on'


@solo_admin
@require_POST
def crear(request):
    errores = _validar(request.POST)
    if errores:
        for e in errores:
            messages.error(request, e)
    else:
        categoria = Categoria()
        _asignar(categoria, request.POST)
        categoria.save()
        messages.success(request, f'Categoría "{categoria.nombre}" creada.')
        registrar(request, 'categorias', 'crear', f'Creó la categoría "{categoria.nombre}".')
    return redirect('categorias:lista')


@solo_admin
@require_POST
def editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    errores = _validar(request.POST, categoria)
    if errores:
        for e in errores:
            messages.error(request, e)
    else:
        _asignar(categoria, request.POST)
        categoria.save()
        messages.success(request, f'Categoría "{categoria.nombre}" actualizada.')
        registrar(request, 'categorias', 'editar', f'Editó la categoría "{categoria.nombre}".')
    return redirect('categorias:lista')


@solo_admin
@require_POST
def eliminar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    try:
        categoria.delete()
        messages.success(request, f'Categoría "{categoria.nombre}" eliminada.')
        registrar(request, 'categorias', 'eliminar', f'Eliminó la categoría "{categoria.nombre}".')
    except ProtectedError:
        messages.error(request, 'No se puede eliminar: tiene materiales asociados. Desactívala en su lugar.')
    return redirect('categorias:lista')
