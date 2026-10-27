import json
from datetime import date

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from apps.entradas.models import Entrada
from apps.salidas.models import Salida
from apps.usuarios.models import Usuario

from .models import Registro

POR_PAGINA = 25


def _fecha(valor):
    try:
        return date.fromisoformat(valor) if valor else None
    except ValueError:
        return None


def _movimientos(request, tipo, estado, usuario_id, desde, hasta, q):
    es_admin = request.user.es_admin
    filas = []

    def filtrar(qs, campo_tercero):
        if not es_admin:
            qs = qs.filter(usuario=request.user)
        elif usuario_id.isdigit():
            qs = qs.filter(usuario_id=int(usuario_id))
        if estado in ('confirmada', 'anulada'):
            qs = qs.filter(estado=estado)
        if desde:
            qs = qs.filter(fecha__gte=desde)
        if hasta:
            qs = qs.filter(fecha__lte=hasta)
        if q:
            filtro = Q(**{f'{campo_tercero}__icontains': q})
            digitos = ''.join(ch for ch in q if ch.isdigit())
            if digitos:
                filtro |= Q(pk=int(digitos))
            qs = qs.filter(filtro)
        return qs

    if tipo in ('', 'entrada'):
        entradas = filtrar(Entrada.objects.select_related('usuario').prefetch_related('detalles__material'), 'proveedor')
        for e in entradas:
            detalles = [{
                'codigo': d.material.codigo, 'material': d.material.nombre,
                'cantidad': f'{d.cantidad:.2f}', 'unidad': d.material.get_unidad_display(),
                'precio': f'{d.costo_unitario:.2f}', 'subtotal': f'{d.subtotal:.2f}',
            } for d in e.detalles.all()]
            total = sum((d.subtotal for d in e.detalles.all()), 0)
            filas.append({
                'tipo': 'entrada', 'numero': e.numero, 'fecha': e.fecha, 'orden': e.creada,
                'tercero': e.proveedor, 'documento': e.documento, 'usuario': e.usuario,
                'estado': e.estado, 'estado_texto': e.get_estado_display(),
                'items': len(detalles), 'total': total, 'detalle_json': json.dumps(detalles),
                'observaciones': e.observaciones, 'pago': '', 'subtotal': total, 'descuento': 0,
            })
    if tipo in ('', 'salida'):
        salidas = filtrar(Salida.objects.select_related('usuario').prefetch_related('detalles__material'), 'cliente')
        for s in salidas:
            detalles = [{
                'codigo': d.material.codigo, 'material': d.material.nombre,
                'cantidad': f'{d.cantidad:.2f}', 'unidad': d.material.get_unidad_display(),
                'precio': f'{d.precio_unitario:.2f}', 'subtotal': f'{d.subtotal:.2f}',
            } for d in s.detalles.all()]
            filas.append({
                'tipo': 'salida', 'numero': s.numero, 'fecha': s.fecha, 'orden': s.creada,
                'tercero': s.cliente, 'documento': s.documento_cliente, 'usuario': s.usuario,
                'estado': s.estado, 'estado_texto': s.get_estado_display(),
                'items': len(detalles), 'total': s.total, 'detalle_json': json.dumps(detalles),
                'observaciones': s.observaciones, 'pago': s.get_metodo_pago_display(),
                'subtotal': s.subtotal, 'descuento': s.descuento,
            })
    filas.sort(key=lambda f: (f['fecha'], f['orden']), reverse=True)
    return filas


@login_required
def lista(request):
    es_admin = request.user.es_admin
    vista = request.GET.get('vista', 'movimientos')
    if vista not in ('movimientos', 'actividad') or (vista == 'actividad' and not es_admin):
        vista = 'movimientos'

    q = request.GET.get('q', '').strip()
    usuario_id = request.GET.get('usuario', '')
    desde = request.GET.get('desde', '')
    hasta = request.GET.get('hasta', '')
    d, h = _fecha(desde), _fecha(hasta)
    ctx = {
        'vista': vista, 'q': q, 'usuario_filtro': usuario_id, 'desde': desde, 'hasta': hasta,
        'usuarios': Usuario.objects.order_by('username') if es_admin else [],
    }

    if vista == 'movimientos':
        tipo = request.GET.get('tipo', '')
        estado = request.GET.get('estado', '')
        filas = _movimientos(request, tipo, estado, usuario_id, d, h, q)
        ctx.update({'pagina': Paginator(filas, POR_PAGINA).get_page(request.GET.get('page')),
                    'tipo_filtro': tipo, 'estado_filtro': estado})
    else:
        modulo = request.GET.get('modulo', '')
        accion = request.GET.get('accion', '')
        registros = Registro.objects.select_related('usuario')
        if q:
            registros = registros.filter(Q(descripcion__icontains=q) | Q(username__icontains=q) | Q(ip__icontains=q))
        if usuario_id.isdigit():
            registros = registros.filter(usuario_id=int(usuario_id))
        if modulo in dict(Registro.MODULOS):
            registros = registros.filter(modulo=modulo)
        if accion in dict(Registro.ACCIONES):
            registros = registros.filter(accion=accion)
        if d:
            registros = registros.filter(fecha__date__gte=d)
        if h:
            registros = registros.filter(fecha__date__lte=h)
        ctx.update({'pagina': Paginator(registros, 50).get_page(request.GET.get('page')),
                    'modulo_filtro': modulo, 'accion_filtro': accion,
                    'modulos': Registro.MODULOS, 'acciones': Registro.ACCIONES})

    params = request.GET.copy()
    params.pop('page', None)
    ctx['query_string'] = params.urlencode()
    return render(request, 'historial/lista.html', ctx)
