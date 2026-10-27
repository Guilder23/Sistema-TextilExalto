(() => {
  const modal = new bootstrap.Modal(document.getElementById('modalEliminar'));
  const form = document.getElementById('formEliminar');

  document.querySelectorAll('.btn-eliminar').forEach((btn) => {
    btn.addEventListener('click', () => {
      const d = window.filaDeBoton(btn).dataset;
      document.getElementById('eliminarNombre').textContent = d.nombre;
      form.action = d.urlEliminar;
      modal.show();
    });
  });
})();
