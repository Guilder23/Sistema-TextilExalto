(() => {
  const modal = new bootstrap.Modal(document.getElementById('modalVer'));
  const poner = (id, valor) => { document.getElementById(id).textContent = valor || '—'; };

  document.querySelectorAll('.btn-ver').forEach((btn) => {
    btn.addEventListener('click', () => {
      const d = window.filaDeBoton(btn).dataset;
      const nombre = `${d.firstName} ${d.lastName}`.trim();
      poner('verAvatar', d.username.charAt(0).toUpperCase());
      poner('verNombre', nombre || d.username);
      poner('verUsername', `@${d.username}`);
      poner('verRol', d.rolDisplay);
      poner('verEstado', d.activo === '1' ? 'Activo' : 'Inactivo');
      poner('verEmail', d.email);
      poner('verTelefono', d.telefono);
      poner('verRegistro', d.registro);
      poner('verAcceso', d.ultimoAcceso);
      modal.show();
    });
  });
})();
