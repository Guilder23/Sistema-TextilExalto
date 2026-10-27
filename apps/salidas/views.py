import json
from datetime import date
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.historial.utils import registrar
from apps.materiales.models import Material
from apps.usuarios.views import solo_admin

from .models import DetalleSalida, Salida

MAX = Decimal('10000000000')
CERO = Decimal('0.00')


def _decimal(valor, minimo_exclusivo=False):
    try:
        n = Decimal((valor or '').strip() or '0')
    except InvalidOperation:
        return None
    if not n.is_finite() or n >= MAX or n < 0 or (minimo_exclusivo and n == 0):
        return None
    return n.quantize(Decimal('0.01'))


@login_required
def lista(request):
    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '')
    pago = request.GET.get('pago', '')
    desde = request.GET.get('desde', '')
    hasta = request.GET.get('hasta', '')
    salidas = Salida.objects.select_related('usuario').prefetch_related('detalles__material')
    if q:
        filtro = Q(cliente__icontains=q) | Q(documento_cliente__icontains=q)
        digitos = ''.join(ch for ch in q if ch.isdigit())
        if digitos:
            filtro |= Q(pk=int(digitos))
        salidas = salidas.filter(filtro)
    if estado in (Salida.CONFIRMADA, Salida.ANULADA):
        salidas = salidas.filter(estado=estado)
    if pago in dict(Salida.PAGOS):
        salidas = salidas.filter(metodo_pago=pago)
    try:
        if desde:
            salidas = salidas.filter(fecha__gte=date.fromisoformat(desde))
        if hasta:
            salidas = salidas.filter(fecha__lte=date.fromisoformat(hasta))
    except ValueError:
        pass

    filas = []
    for s in salidas:
        detalles = [{
            'codigo': d.material.codigo, 'material': d.material.nombre,
            'cantidad': f'{d.cantidad:.2f}', 'unidad': d.material.get_unidad_display(),
            'precio': f'{d.precio_unitario:.2f}', 'subtotal': f'{d.subtotal:.2f}',
        } for d in s.detalles.all()]
        s.items = len(detalles)
        s.detalle_json = json.dumps(detalles)
        filas.append(s)

    return render(request, 'salidas/lista.html', {
        'salidas': filas,
        'materiales': Material.objects.filter(activo=True).order_by('nombre'),
        'pagos': Salida.PAGOS,
        'q': q, 'estado_filtro': estado, 'pago_filtro': pago, 'desde': desde, 'hasta': hasta,
        'hoy': date.today().isoformat(),
    })


@login_required
@require_POST
def crear(request):
    datos = request.POST
    errores = []
    try:
        fecha = date.fromisoformat(datos.get('fecha', ''))
    except ValueError:
        fecha = None
        errores.append('La fecha es inválida.')
    cliente = datos.get('cliente', '').strip()
    if not cliente:
        errores.append('El cliente es obligatorio.')
    pago = datos.get('metodo_pago', '')
    if pago not in dict(Salida.PAGOS):
        errores.append('Selecciona un método de pago válido.')
    descuento = _decimal(datos.get('descuento', ''))
    if descuento is None:
        errores.append('El descuento no es válido.')

    ids = datos.getlist('material')
    cantidades = datos.getlist('cantidad')
    precios = datos.getlist('precio')
    lineas = {}
    if not ids or not (len(ids) == len(cantidades) == len(precios)):
        errores.append('Agrega al menos un material.')
    else:
        for i, (mid, cant, precio) in enumerate(zip(ids, cantidades, precios), start=1):
            cantidad = _decimal(cant, minimo_exclusivo=True)
            precio_u = _decimal(precio)
            if not mid.isdigit():
                errores.append(f'Línea {i}: selecciona un material.')
            elif cantidad is None:
                errores.append(f'Línea {i}: la cantidad debe ser mayor a 0.')
            elif precio_u is None:
                errores.append(f'Línea {i}: el precio no es válido.')
            elif int(mid) in lineas:
                errores.append(f'Línea {i}: el material está repetido.')
            else:
                lineas[int(mid)] = (cantidad, precio_u)

    advertencias = []
    salida = None
    if not errores:
        with transaction.atomic():
            materiales = {m.pk: m for m in Material.objects.select_for_update().filter(pk__in=lineas)}
            if len(materiales) != len(lineas) or any(not m.activo for m in materiales.values()):
                errores.append('Todos los materiales deben existir y estar activos.')
            else:
                for mid, (cantidad, _) in lineas.items():
                    m = materiales[mid]
                    if cantidad > m.stock_actual:
                        errores.append(
                            f'Stock insuficiente de "{m.nombre}": disponible {m.stock_actual:.2f}, solicitado {cantidad:.2f}.')
                subtotal = sum((c * p for c, p in lineas.values()), CERO)
                if not errores and descuento > subtotal:
                    errores.append('El descuento no puede ser mayor que el subtotal.')
            if not errores:
                salida = Salida.objects.create(
                    fecha=fecha, cliente=cliente, documento_cliente=datos.get('documento_cliente', '').strip(),
                    telefono_cliente=datos.get('telefono_cliente', '').strip(), metodo_pago=pago,
                    subtotal=subtotal, descuento=descuento, total=subtotal - descuento,
                    observaciones=datos.get('observaciones', '').strip(), usuario=request.user)
                for mid, (cantidad, precio_u) in lineas.items():
                    m = materiales[mid]
                    DetalleSalida.objects.create(
                        salida=salida, material=m, cantidad=cantidad,
                        precio_unitario=precio_u, costo_unitario=m.costo_compra)
                    m.stock_actual -= cantidad
                    m.save(update_fields=['stock_actual', 'actualizado'])
                    if m.nivel_stock != 'verde':
                        advertencias.append(f'"{m.nombre}" quedó en nivel {m.nivel_stock} ({m.stock_actual:.2f}).')
    if salida:
        messages.success(request, f'Venta {salida.numero} registrada por {salida.total:.2f}. Existencias actualizadas.')
        registrar(request, 'salidas', 'crear', f'Registró la venta {salida.numero} (cliente: {salida.cliente}, total: {salida.total:.2f}).')
        for a in advertencias:
            messages.warning(request, a)
    for e in errores:
        messages.error(request, e)
    return redirect('salidas:lista')


@solo_admin
@require_POST
def anular(request, pk):
    with transaction.atomic():
        salida = get_object_or_404(Salida.objects.select_for_update(), pk=pk)
        if salida.estado == Salida.ANULADA:
            messages.error(request, 'La venta ya está anulada.')
            return redirect('salidas:lista')
        detalles = list(salida.detalles.all())
        materiales = {m.pk: m for m in Material.objects.select_for_update().filter(
            pk__in=[d.material_id for d in detalles])}
        for d in detalles:
            m = materiales[d.material_id]
            m.stock_actual += d.cantidad
            m.save(update_fields=['stock_actual', 'actualizado'])
        salida.estado = Salida.ANULADA
        salida.save(update_fields=['estado'])
    messages.success(request, f'Venta {salida.numero} anulada. Existencias devueltas.')
    registrar(request, 'salidas', 'anular', f'Anuló la venta {salida.numero}.')
    return redirect('salidas:lista')
