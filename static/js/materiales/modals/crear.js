(() => {
  const form = document.getElementById('formCrear');
  form.addEventListener('submit', (e) => {
    if (!form.checkValidity()) {
      e.preventDefault();
      form.reportValidity();
    }
  });
  document.getElementById('modalCrear').addEventListener('hidden.bs.modal', () => form.reset());
})();
