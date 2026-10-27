from datetime import date
from decimal import Decimal
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from apps.materiales.models import Material
from apps.salidas.models import Salida


def _fecha(value):
    try:
        return date.fromisoformat(value) if value else None
    except ValueError:
        return None


def _filtros_ventas(request):
    desde = request.GET.get('desde', '').strip()
    hasta = request.GET.get('hasta', '').strip()
    estado = request.GET.get('estado', '').strip()
    pago = request.GET.get('pago', '').strip()
    q = request.GET.get('q', '').strip()
    ventas = Salida.objects.select_related('usuario').prefetch_related('detalles__material')
    if not request.user.es_admin:
        ventas = ventas.filter(usuario=request.user)
    if _fecha(desde):
        ventas = ventas.filter(fecha__gte=_fecha(desde))
    if _fecha(hasta):
        ventas = ventas.filter(fecha__lte=_fecha(hasta))
    if estado in dict(Salida.ESTADOS):
        ventas = ventas.filter(estado=estado)
    if pago in dict(Salida.PAGOS):
        ventas = ventas.filter(metodo_pago=pago)
    if q:
        filtro = Q(cliente__icontains=q) | Q(documento_cliente__icontains=q)
        digitos = ''.join(c for c in q if c.isdigit())
        if digitos:
            filtro |= Q(pk=int(digitos))
        ventas = ventas.filter(filtro)
    return ventas, {'desde': desde, 'hasta': hasta, 'estado': estado, 'pago': pago, 'q': q}


def _filtros_materiales(request):
    q = request.GET.get('q', '').strip()
    nivel = request.GET.get('nivel', '').strip()
    activo = request.GET.get('activo', '').strip()
    materiales = Material.objects.select_related('categoria')
    if q:
        materiales = materiales.filter(Q(codigo__icontains=q) | Q(nombre__icontains=q) | Q(categoria__nombre__icontains=q))
    if activo in ('1', '0'):
        materiales = materiales.filter(activo=activo == '1')
    return materiales, {'q': q, 'nivel': nivel, 'activo': activo}


@login_required
def lista(request):
    pestaña = request.GET.get('tab', 'materiales')
    if pestaña not in ('materiales', 'ventas'):
        pestaña = 'materiales'
    contexto = {'tab': pestaña, 'materiales_niveles': ('verde', 'amarillo', 'rojo', 'inactivo'),
                'pagos': Salida.PAGOS, 'estados': Salida.ESTADOS}
    if pestaña == 'materiales':
        materiales, filtros = _filtros_materiales(request)
        rows = []
        for material in materiales:
            nivel = 'inactivo' if not material.activo else material.nivel_stock
            if filtros['nivel'] in ('verde', 'amarillo', 'rojo', 'inactivo') and nivel != filtros['nivel']:
                continue
            rows.append({'material': material, 'nivel': nivel,
                         'valor_stock': material.stock_actual * material.costo_compra})
        contexto.update({'filas': rows, 'filtros': filtros})
    else:
        ventas, filtros = _filtros_ventas(request)
        ventas = list(ventas)
        contexto.update({
            'ventas': ventas,
            'filtros': filtros,
            'total_ventas': sum((v.total for v in ventas if v.estado == Salida.CONFIRMADA), Decimal('0')),
            'cantidad_ventas': len(ventas),
            'confirmadas': sum(1 for v in ventas if v.estado == Salida.CONFIRMADA),
            'anuladas': sum(1 for v in ventas if v.estado == Salida.ANULADA),
        })
    return render(request, 'reportes/lista.html', contexto)


def _pdf_response(buffer, filename):
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def _pdf_base(title, subtitle):
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=12 * mm,
                                 leftMargin=12 * mm, topMargin=12 * mm, bottomMargin=12 * mm)
    styles = getSampleStyleSheet()
    story = [Paragraph('TEXTIL EXALTO', styles['Title']), Paragraph(title, styles['Heading2']),
             Paragraph(subtitle, styles['Normal']), Spacer(1, 8 * mm)]
    return buffer, document, story, styles


@login_required
def pdf_materiales(request):
    materiales, filtros = _filtros_materiales(request)
    rows = [['Código', 'Material', 'Categoría', 'Unidad', 'Stock', 'Alerta', 'Costo compra', 'Precio venta', 'Valor stock', 'Estado']]
    for material in materiales:
        nivel = 'Inactivo' if not material.activo else material.nivel_stock.capitalize()
        if filtros['nivel'] and nivel.lower() != filtros['nivel']:
            continue
        rows.append([material.codigo, material.nombre, material.categoria.nombre, material.get_unidad_display(),
                     f'{material.stock_actual:.2f}', f'{material.stock_minimo:.2f} / {material.stock_critico:.2f}',
                     f'{material.costo_compra:.2f}', f'{material.precio_venta:.2f}',
                     f'{material.stock_actual * material.costo_compra:.2f}', nivel])
    buffer, document, story, styles = _pdf_base('Reporte de materiales',
        f'Generado el {date.today():%d/%m/%Y} · Filtros aplicados: {filtros["q"] or "ninguno"}')
    table = Table(rows, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), .25, colors.HexColor('#cbd5e1')), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
    ]))
    story.append(table)
    document.build(story)
    return _pdf_response(buffer, 'reporte-materiales.pdf')


@login_required
def pdf_ventas(request):
    ventas, filtros = _filtros_ventas(request)
    rows = [['Número', 'Fecha', 'Cliente', 'Vendedor', 'Pago', 'Ítems', 'Subtotal', 'Descuento', 'Total', 'Estado']]
    total = Decimal('0')
    for venta in ventas:
        total += venta.total if venta.estado == Salida.CONFIRMADA else Decimal('0')
        rows.append([venta.numero, venta.fecha.strftime('%d/%m/%Y'), venta.cliente, venta.usuario.username,
                     venta.get_metodo_pago_display(), str(venta.detalles.count()), f'{venta.subtotal:.2f}',
                     f'{venta.descuento:.2f}', f'{venta.total:.2f}', venta.get_estado_display()])
    rows.append(['', '', '', '', '', '', '', 'TOTAL CONFIRMADO', f'{total:.2f}', ''])
    buffer, document, story, styles = _pdf_base('Reporte de salidas / ventas',
        f'Generado el {date.today():%d/%m/%Y} · Usuario: {request.user.username} · Registros: {len(rows) - 2}')
    table = Table(rows, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), .25, colors.HexColor('#cbd5e1')), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8fafc')]),
        ('FONTNAME', (7, -1), (8, -1), 'Helvetica-Bold'), ('BACKGROUND', (7, -1), (8, -1), colors.HexColor('#e0e7ff')),
    ]))
    story.append(table)
    document.build(story)
    return _pdf_response(buffer, 'reporte-salidas-ventas.pdf')
