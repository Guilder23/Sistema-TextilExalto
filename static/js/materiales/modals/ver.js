(() => {
  const modal = new bootstrap.Modal(document.getElementById('modalVer'));
  const poner = (id, valor) => { document.getElementById(id).textContent = valor || '—'; };

  document.querySelectorAll('.btn-ver').forEach((btn) => {
    btn.addEventListener('click', () => {
      const d = window.filaDeBoton(btn).dataset;
      poner('verNombre', d.nombre);
      poner('verCodigo', d.codigo);
      poner('verCategoria', d.categoriaNombre);
      poner('verUnidad', d.unidadDisplay);
      poner('verStock', `${d.stockActual} ${d.unidadDisplay}`);
      poner('verStockMinimo', `${d.stockMinimo} ${d.unidadDisplay}`);
      poner('verCosto', d.costo);
      poner('verEstado', d.activo === '1' ? 'Activo' : 'Inactivo');
      poner('verDescripcion', d.descripcion);
      poner('verCreado', d.creado);
      poner('verActualizado', d.actualizado);
      modal.show();
    });
  });
})();
