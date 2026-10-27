(() => {
  const modal = new bootstrap.Modal(document.getElementById('modalVer'));
  const poner = (id, valor) => { document.getElementById(id).textContent = valor || '—'; };

  document.querySelectorAll('.btn-ver').forEach((btn) => {
    btn.addEventListener('click', () => {
      const d = window.filaDeBoton(btn).dataset;
      poner('verNombre', d.nombre);
      poner('verDescripcion', d.descripcion);
      poner('verEstado', d.activa === '1' ? 'Activa' : 'Inactiva');
      poner('verMateriales', d.materiales);
      poner('verCreada', d.creada);
      modal.show();
    });
  });
})();
