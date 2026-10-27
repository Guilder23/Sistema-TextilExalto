// Los filtros se envían por GET; los selects y fechas aplican al pulsar "Filtrar".
document.querySelectorAll('form select[name="tipo"], form select[name="usuario"]').forEach((el) => {
  el.addEventListener('change', () => el.form.submit());
});
