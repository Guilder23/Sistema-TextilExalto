(() => {
  const modalEl = document.getElementById('modalCrear');
  const form = document.getElementById('formCrear');
  const cuerpo = document.getElementById('lineas');
  const plantilla = document.getElementById('plantillaLinea');
  const totalEl = document.getElementById('totalEntrada');
  const errorEl = document.getElementById('errorLineas');

  const recalcular = () => {
    let total = 0;
    cuerpo.querySelectorAll('.linea').forEach((fila) => {
      const sub = (parseFloat(fila.querySelector('.linea-cantidad').value) || 0)
        * (parseFloat(fila.querySelector('.linea-costo').value) || 0);
      fila.querySelector('.linea-subtotal').textContent = sub.toFixed(2);
      total += sub;
    });
    totalEl.textContent = total.toFixed(2);
  };

  const agregarLinea = () => {
    const fila = plantilla.content.firstElementChild.cloneNode(true);
    const select = fila.querySelector('.linea-material');
    select.addEventListener('change', () => {
      const opcion = select.selectedOptions[0];
      fila.querySelector('.linea-unidad').textContent = opcion.dataset.unidad || '—';
      if (opcion.value) fila.querySelector('.linea-costo').value = opcion.dataset.costo;
      recalcular();
    });
    fila.querySelector('.linea-cantidad').addEventListener('input', recalcular);
    fila.querySelector('.linea-costo').addEventListener('input', recalcular);
    fila.querySelector('.linea-quitar').addEventListener('click', () => {
      fila.remove();
      recalcular();
    });
    cuerpo.appendChild(fila);
  };

  const reiniciar = () => {
    form.reset();
    cuerpo.innerHTML = '';
    errorEl.textContent = '';
    agregarLinea();
    recalcular();
  };

  document.getElementById('btnAgregarLinea').addEventListener('click', agregarLinea);
  modalEl.addEventListener('hidden.bs.modal', reiniciar);

  form.addEventListener('submit', (e) => {
    errorEl.textContent = '';
    const materiales = [...cuerpo.querySelectorAll('.linea-material')].map((s) => s.value);
    if (!materiales.length) {
      errorEl.textContent = 'Agrega al menos un material.';
    } else if (new Set(materiales).size !== materiales.length) {
      errorEl.textContent = 'No repitas el mismo material en varias líneas.';
    }
    if (errorEl.textContent || !form.checkValidity()) {
      e.preventDefault();
      form.reportValidity();
    }
  });

  reiniciar();
})();
