(() => {
  const form = document.getElementById('formCrear');
  form.addEventListener('submit', (e) => {
    const alerta = document.getElementById('crearStockMinimo');
    const critico = document.getElementById('crearStockCritico');
    const invalido = parseFloat(critico.value) > parseFloat(alerta.value);
    critico.classList.toggle('is-invalid', invalido);
    if (invalido || !form.checkValidity()) {
      e.preventDefault();
      form.reportValidity();
    }
  });
  document.getElementById('modalCrear').addEventListener('hidden.bs.modal', () => form.reset());
})();
