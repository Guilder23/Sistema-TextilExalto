(() => {
  const modal = new bootstrap.Modal(document.getElementById('modalVer'));
  const poner = (id, valor) => { document.getElementById(id).textContent = valor || '—'; };
  const celda = (texto, clase = '') => {
    const td = document.createElement('td');
    td.textContent = texto;
    if (clase) td.className = clase;
    return td;
  };

  document.querySelectorAll('.btn-ver').forEach((btn) => {
    btn.addEventListener('click', () => {
      const d = window.filaDeBoton(btn).dataset;
      poner('verNumero', d.numero);
      poner('verFecha', d.fecha);
      poner('verCliente', d.cliente);
      poner('verDocumento', d.documento);
      poner('verTelefono', d.telefono);
      poner('verPago', d.pago);
      poner('verUsuario', d.usuario);
      poner('verEstado', d.estado);
      poner('verObservaciones', d.observaciones);
      poner('verSubtotal', d.subtotal);
      poner('verDescuento', d.descuento);
      poner('verTotal', d.total);

      const cuerpo = document.getElementById('verDetalle');
      cuerpo.innerHTML = '';
      JSON.parse(d.detalle).forEach((l) => {
        const tr = document.createElement('tr');
        tr.append(celda(l.codigo), celda(l.material), celda(`${l.cantidad} ${l.unidad}`, 'text-end'),
          celda(l.precio, 'text-end'), celda(l.subtotal, 'text-end'));
        cuerpo.appendChild(tr);
      });
      modal.show();
    });
  });
})();
