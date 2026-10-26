(() => {
  const form = document.getElementById('formCrear');
  const p1 = document.getElementById('crearPassword');
  const p2 = document.getElementById('crearPassword2');

  form.addEventListener('submit', (e) => {
    const coincide = p1.value === p2.value;
    p2.classList.toggle('is-invalid', !coincide);
    if (!coincide || !form.checkValidity()) {
      e.preventDefault();
      form.reportValidity();
    }
  });

  document.getElementById('modalCrear').addEventListener('hidden.bs.modal', () => {
    form.reset();
    p2.classList.remove('is-invalid');
  });
})();
