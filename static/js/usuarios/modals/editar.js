(() => {
  const modalEl = document.getElementById('modalEditar');
  const modal = new bootstrap.Modal(modalEl);
  const form = document.getElementById('formEditar');
  const p1 = document.getElementById('editarPassword');
  const p2 = document.getElementById('editarPassword2');
  const campos = {
    username: 'editarUsername', firstName: 'editarNombre', lastName: 'editarApellido',
    email: 'editarEmail', telefono: 'editarTelefono', rol: 'editarRol',
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
    const coincide = p1.value === p2.value;
    p2.classList.toggle('is-invalid', !coincide);
    if (!coincide || !form.checkValidity()) {
      e.preventDefault();
      form.reportValidity();
    }
  });

  modalEl.addEventListener('hidden.bs.modal', () => {
    p1.value = '';
    p2.value = '';
    p2.classList.remove('is-invalid');
  });
})();
