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
  document.getElementById('modalCrear').addEventListener('hidden.bs.modal', () => {
    form.reset();
    vista.src = '';
    vista.classList.add('d-none');
    document.getElementById('crearImagenSinVista').classList.remove('d-none');
  });
  const imagen = document.getElementById('crearImagen');
  const vista = document.getElementById('crearImagenVista');
  const sinVista = document.getElementById('crearImagenSinVista');
  imagen.addEventListener('change', () => {
    const archivo = imagen.files[0];
    if (!archivo) {
      vista.src = '';
      vista.classList.add('d-none');
      sinVista.classList.remove('d-none');
      return;
    }
    vista.src = URL.createObjectURL(archivo);
    vista.classList.remove('d-none');
    sinVista.classList.add('d-none');
  });
})();
