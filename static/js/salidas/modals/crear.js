(() => {
  const modalEl = document.getElementById('modalCrear');
  const form = document.getElementById('formCrear');
  const cuerpo = document.getElementById('lineas');
  const plantilla = document.getElementById('plantillaLinea');
  const descuentoEl = document.getElementById('crearDescuento');
  const errorEl = document.getElementById('errorLineas');

  const validarCantidad = (fila) => {
    const opcion = fila.querySelector('.linea-material').selectedOptions[0];
    const cantidad = parseFloat(fila.querySelector('.linea-cantidad').value) || 0;
    const stock = parseFloat(opcion.dataset.stock);
    const excede = opcion.value !== '' && cantidad > stock;
    fila.querySelector('.linea-cantidad').classList.toggle('is-invalid', excede);
    return !excede;
  };

  const recalcular = () => {
    let subtotal = 0;
    cuerpo.querySelectorAll('.linea').forEach((fila) => {
      const sub = (parseFloat(fila.querySelector('.linea-cantidad').value) || 0)
        * (parseFloat(fila.querySelector('.linea-precio').value) || 0);
      fila.querySelector('.linea-subtotal').textContent = sub.toFixed(2);
      subtotal += sub;
    });
    const descuento = parseFloat(descuentoEl.value) || 0;
    document.getElementById('subtotalVenta').textContent = subtotal.toFixed(2);
    document.getElementById('totalVenta').textContent = Math.max(0, subtotal - descuento).toFixed(2);
    descuentoEl.classList.toggle('is-invalid', descuento > subtotal);
  };

  const agregarLinea = () => {
    const fila = plantilla.content.firstElementChild.cloneNode(true);
    const select = fila.querySelector('.linea-material');
    select.addEventListener('change', () => {
      const o = select.selectedOptions[0];
      fila.querySelector('.linea-unidad').textContent = o.dataset.unidad || '—';
      fila.querySelector('.linea-disponible').textContent = o.value ? `${o.dataset.stock} ${o.dataset.unidad}` : '—';
      if (o.value) fila.querySelector('.linea-precio').value = o.dataset.precio;
      validarCantidad(fila);
      recalcular();
    });
    fila.querySelector('.linea-cantidad').addEventListener('input', () => { validarCantidad(fila); recalcular(); });
    fila.querySelector('.linea-precio').addEventListener('input', recalcular);
    fila.querySelector('.linea-quitar').addEventListener('click', () => { fila.remove(); recalcular(); });
    cuerpo.appendChild(fila);
  };

  const reiniciar = () => {
    form.reset();
    cuerpo.innerHTML = '';
    errorEl.textContent = '';
    descuentoEl.classList.remove('is-invalid');
    agregarLinea();
    recalcular();
  };

  document.getElementById('btnAgregarLinea').addEventListener('click', agregarLinea);
  descuentoEl.addEventListener('input', recalcular);
  modalEl.addEventListener('hidden.bs.modal', reiniciar);

  form.addEventListener('submit', (e) => {
    errorEl.textContent = '';
    const materiales = [...cuerpo.querySelectorAll('.linea-material')].map((s) => s.value);
    const stockOk = [...cuerpo.querySelectorAll('.linea')].every(validarCantidad);
    if (!materiales.length) {
      errorEl.textContent = 'Agrega al menos un material.';
    } else if (new Set(materiales).size !== materiales.length) {
      errorEl.textContent = 'No repitas el mismo material en varias líneas.';
    } else if (!stockOk) {
      errorEl.textContent = 'Hay cantidades que superan el stock disponible.';
    } else if (descuentoEl.classList.contains('is-invalid')) {
      errorEl.textContent = 'El descuento no puede ser mayor que el subtotal.';
    }
    if (errorEl.textContent || !form.checkValidity()) {
      e.preventDefault();
      form.reportValidity();
    }
  });

  reiniciar();
})();
