from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import F, Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.categorias.models import Categoria
from apps.usuarios.views import solo_admin

from .models import Material


@login_required
def lista(request):
    q = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '')
    estado = request.GET.get('estado', '')
    materiales = Material.objects.select_related('categoria')
    if q:
        materiales = materiales.filter(
            Q(codigo__icontains=q) | Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    if categoria.isdigit():
        materiales = materiales.filter(categoria_id=categoria)
    if estado == 'rojo':
        materiales = materiales.filter(stock_actual__lte=F('stock_critico'))
    elif estado == 'amarillo':
        materiales = materiales.filter(stock_actual__lte=F('stock_minimo'), stock_actual__gt=F('stock_critico'))
    elif estado == 'verde':
        materiales = materiales.filter(stock_actual__gt=F('stock_minimo')).filter(stock_actual__gt=F('stock_critico'))
    elif estado == 'inactivo':
        materiales = materiales.filter(activo=False)
    return render(request, 'materiales/lista.html', {
        'materiales': materiales,
        'categorias': Categoria.objects.filter(activa=True),
        'todas_categorias': Categoria.objects.all(),
        'unidades': Material.UNIDADES,
        'q': q, 'categoria_filtro': categoria, 'estado_filtro': estado,
    })


def _numero(valor, etiqueta, errores):
    try:
        n = Decimal(valor.strip() or '0')
        if n < 0 or n >= Decimal('10000000000'):
            raise InvalidOperation
        return n.quantize(Decimal('0.01'))
    except (InvalidOperation, AttributeError):
        errores.append(f'{etiqueta} debe ser un número válido mayor o igual a 0.')
        return None


def _validar(datos, material=None):
    errores = []
    codigo = datos.get('codigo', '').strip()
    if not codigo:
        errores.append('El código es obligatorio.')
    elif Material.objects.filter(codigo__iexact=codigo).exclude(pk=getattr(material, 'pk', None)).exists():
        errores.append('Ya existe un material con ese código.')
    if not datos.get('nombre', '').strip():
        errores.append('El nombre es obligatorio.')
    if not Categoria.objects.filter(pk=datos.get('categoria') or 0).exists():
        errores.append('Selecciona una categoría válida.')
    if datos.get('unidad') not in dict(Material.UNIDADES):
        errores.append('Unidad inválida.')
    minimo = _numero(datos.get('stock_minimo', ''), 'El stock de alerta', errores)
    critico = _numero(datos.get('stock_critico', ''), 'El stock crítico', errores)
    if minimo is not None and critico is not None and critico > minimo:
        errores.append('El stock crítico no puede ser mayor que el stock de alerta.')
    _numero(datos.get('costo_compra', ''), 'El costo de compra', errores)
    _numero(datos.get('precio_venta', ''), 'El precio de venta', errores)
    return errores


def _asignar(material, datos):
    material.codigo = datos['codigo'].strip()
    material.nombre = datos['nombre'].strip()
    material.descripcion = datos.get('descripcion', '').strip()
    material.categoria_id = int(datos['categoria'])
    material.unidad = datos['unidad']
    material.stock_minimo = _numero(datos['stock_minimo'], '', [])
    material.stock_critico = _numero(datos['stock_critico'], '', [])
    material.costo_compra = _numero(datos['costo_compra'], '', [])
    material.precio_venta = _numero(datos['precio_venta'], '', [])
    material.activo = datos.get('activo') == 'on'


def _guardar(request, material, mensaje):
    errores = _validar(request.POST, material if material.pk else None)
    if not errores:
        try:
            _asignar(material, request.POST)
            material.save()
        except IntegrityError:
            errores.append('Ya existe un material con ese código.')
    if errores:
        for e in errores:
            messages.error(request, e)
    else:
        messages.success(request, f'Material "{material.nombre}" {mensaje}.')
    return redirect('materiales:lista')


@solo_admin
@require_POST
def crear(request):
    return _guardar(request, Material(), 'registrado')


@solo_admin
@require_POST
def editar(request, pk):
    return _guardar(request, get_object_or_404(Material, pk=pk), 'actualizado')


@solo_admin
@require_POST
def eliminar(request, pk):
    material = get_object_or_404(Material, pk=pk)
    try:
        material.delete()
        messages.success(request, f'Material "{material.nombre}" eliminado.')
    except ProtectedError:
        messages.error(request, 'No se puede eliminar: tiene movimientos asociados. Desactívalo en su lugar.')
    return redirect('materiales:lista')

