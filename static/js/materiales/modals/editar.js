(() => {
  const modal = new bootstrap.Modal(document.getElementById('modalEditar'));
  const form = document.getElementById('formEditar');
  const campos = {
    codigo: 'editarCodigo', nombre: 'editarNombre', descripcion: 'editarDescripcion',
    categoria: 'editarCategoria', unidad: 'editarUnidad',
    stockMinimo: 'editarStockMinimo', costo: 'editarCosto',
  };

  document.querySelectorAll('.btn-editar').forEach((btn) => {
    btn.addEventListener('click', () => {
      const d = window.filaDeBoton(btn).dataset;
      for (const [clave, id] of Object.entries(campos)) {
        document.getElementById(id).value = d[clave] || '';
      }
      document.getElementById('editarActivo').checked = d.activo === '1';
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
