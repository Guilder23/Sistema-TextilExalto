(() => {
  const modal = new bootstrap.Modal(document.getElementById('modalEditar'));
  const form = document.getElementById('formEditar');

  document.querySelectorAll('.btn-editar').forEach((btn) => {
    btn.addEventListener('click', () => {
      const d = window.filaDeBoton(btn).dataset;
      document.getElementById('editarNombre').value = d.nombre;
      document.getElementById('editarDescripcion').value = d.descripcion;
      document.getElementById('editarActiva').checked = d.activa === '1';
      form.action = d.urlEditar;
      modal.show();
    });
  });

  form.addEventListener('submit', (e) => {
    if (!form.checkValidity()) {
      e.preventDefault();
      form.reportValidity();
    }
  });
})();
