import json
from datetime import date
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.historial.utils import registrar
from apps.materiales.models import Material
from apps.usuarios.views import solo_admin

from .models import DetalleEntrada, Entrada

MAX = Decimal('10000000000')


def _decimal(valor, minimo_exclusivo=False):
    try:
        n = Decimal((valor or '').strip())
    except InvalidOperation:
        return None
    if not n.is_finite() or n >= MAX or n < 0 or (minimo_exclusivo and n == 0):
        return None
    return n.quantize(Decimal('0.01'))


@solo_admin
def lista(request):
    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '')
    desde = request.GET.get('desde', '')
    hasta = request.GET.get('hasta', '')
    entradas = Entrada.objects.select_related('usuario').prefetch_related('detalles__material')
    if q:
        filtro = Q(proveedor__icontains=q) | Q(documento__icontains=q)
        digitos = ''.join(ch for ch in q if ch.isdigit())
        if digitos:
            filtro |= Q(pk=int(digitos))
        entradas = entradas.filter(filtro)
    if estado in (Entrada.CONFIRMADA, Entrada.ANULADA):
        entradas = entradas.filter(estado=estado)
    try:
        if desde:
            entradas = entradas.filter(fecha__gte=date.fromisoformat(desde))
        if hasta:
            entradas = entradas.filter(fecha__lte=date.fromisoformat(hasta))
    except ValueError:
        pass

    filas = []
    for e in entradas:
        detalles = [{
            'material': d.material.nombre, 'codigo': d.material.codigo,
            'cantidad': f'{d.cantidad:.2f}', 'costo': f'{d.costo_unitario:.2f}',
            'subtotal': f'{d.subtotal:.2f}',
        } for d in e.detalles.all()]
        e.total = sum((d.subtotal for d in e.detalles.all()), Decimal('0'))
        e.items = len(detalles)
        e.detalle_json = json.dumps(detalles)
        filas.append(e)

    return render(request, 'entradas/lista.html', {
        'entradas': filas,
        'materiales': Material.objects.filter(activo=True).order_by('nombre'),
        'q': q, 'estado_filtro': estado, 'desde': desde, 'hasta': hasta,
        'hoy': date.today().isoformat(),
    })


@solo_admin
@require_POST
def crear(request):
    datos = request.POST
    errores = []
    try:
        fecha = date.fromisoformat(datos.get('fecha', ''))
    except ValueError:
        fecha = None
        errores.append('La fecha es inválida.')
    proveedor = datos.get('proveedor', '').strip()
    if not proveedor:
        errores.append('El proveedor es obligatorio.')

    ids = datos.getlist('material')
    cantidades = datos.getlist('cantidad')
    costos = datos.getlist('costo')
    lineas = {}
    if not ids or not (len(ids) == len(cantidades) == len(costos)):
        errores.append('Agrega al menos un material.')
    else:
        for i, (mid, cant, costo) in enumerate(zip(ids, cantidades, costos), start=1):
            cantidad = _decimal(cant, minimo_exclusivo=True)
            costo_u = _decimal(costo)
            if not mid.isdigit():
                errores.append(f'Línea {i}: selecciona un material.')
            elif cantidad is None:
                errores.append(f'Línea {i}: la cantidad debe ser mayor a 0.')
            elif costo_u is None:
                errores.append(f'Línea {i}: el costo no es válido.')
            elif int(mid) in lineas:
                errores.append(f'Línea {i}: el material está repetido.')
            else:
                lineas[int(mid)] = (cantidad, costo_u)

    if not errores:
        with transaction.atomic():
            materiales = {m.pk: m for m in Material.objects.select_for_update().filter(pk__in=lineas)}
            if len(materiales) != len(lineas) or any(not m.activo for m in materiales.values()):
                errores.append('Todos los materiales deben existir y estar activos.')
            else:
                entrada = Entrada.objects.create(
                    fecha=fecha, proveedor=proveedor, documento=datos.get('documento', '').strip(),
                    observaciones=datos.get('observaciones', '').strip(), usuario=request.user)
                for mid, (cantidad, costo_u) in lineas.items():
                    material = materiales[mid]
                    DetalleEntrada.objects.create(
                        entrada=entrada, material=material, cantidad=cantidad, costo_unitario=costo_u)
                    material.stock_actual += cantidad
                    material.costo_compra = costo_u
                    material.save(update_fields=['stock_actual', 'costo_compra', 'actualizado'])
                messages.success(request, f'Entrada {entrada.numero} registrada. Existencias actualizadas.')
                registrar(request, 'entradas', 'crear', f'Registró la entrada {entrada.numero} (proveedor: {entrada.proveedor}).')
    for e in errores:
        messages.error(request, e)
    return redirect('entradas:lista')


@solo_admin
@require_POST
def anular(request, pk):
    with transaction.atomic():
        entrada = get_object_or_404(Entrada.objects.select_for_update(), pk=pk)
        if entrada.estado == Entrada.ANULADA:
            messages.error(request, 'La entrada ya está anulada.')
            return redirect('entradas:lista')
        detalles = list(entrada.detalles.select_related('material'))
        materiales = {m.pk: m for m in Material.objects.select_for_update().filter(
            pk__in=[d.material_id for d in detalles])}
        faltantes = [d.material.nombre for d in detalles if materiales[d.material_id].stock_actual < d.cantidad]
        if faltantes:
            messages.error(request, 'No se puede anular: el stock actual no alcanza para revertir ' + ', '.join(faltantes) + '.')
            return redirect('entradas:lista')
        for d in detalles:
            m = materiales[d.material_id]
            m.stock_actual -= d.cantidad
            m.save(update_fields=['stock_actual', 'actualizado'])
        entrada.estado = Entrada.ANULADA
        entrada.save(update_fields=['estado'])
    messages.success(request, f'Entrada {entrada.numero} anulada. Existencias revertidas.')
    registrar(request, 'entradas', 'anular', f'Anuló la entrada {entrada.numero}.')
    return redirect('entradas:lista')
