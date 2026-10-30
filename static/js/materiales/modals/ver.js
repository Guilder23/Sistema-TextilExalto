(() => {
  const modal = new bootstrap.Modal(document.getElementById('modalVer'));
  const poner = (id, valor) => { document.getElementById(id).textContent = valor || '—'; };

  document.querySelectorAll('.btn-ver').forEach((btn) => {
    btn.addEventListener('click', () => {
      const d = window.filaDeBoton(btn).dataset;
      const imagen = document.getElementById('verImagen');
      const sinImagen = document.getElementById('verSinImagen');
      imagen.src = d.imagen || '';
      imagen.classList.toggle('d-none', !d.imagen);
      sinImagen.classList.toggle('d-none', !!d.imagen);
      poner('verNombre', d.nombre);
      poner('verCodigo', d.codigo);
      poner('verCategoria', d.categoriaNombre);
      poner('verUnidad', d.unidadDisplay);
      poner('verStock', `${d.stockActual} ${d.unidadDisplay}`);
      poner('verStockMinimo', `${d.stockMinimo} ${d.unidadDisplay}`);
      poner('verStockCritico', `${d.stockCritico} ${d.unidadDisplay}`);
      const niveles = { rojo: 'Crítico', amarillo: 'En alerta', verde: 'Suficiente' };
      poner('verNivel', niveles[d.nivel]);
      document.getElementById('verSemaforo').className = `semaforo semaforo-${d.nivel}`;
      poner('verCostoCompra', d.costoCompra);
      poner('verPrecioVenta', d.precioVenta);
      poner('verEstado', d.activo === '1' ? 'Activo' : 'Inactivo');
      poner('verDescripcion', d.descripcion);
      poner('verCreado', d.creado);
      poner('verActualizado', d.actualizado);
      modal.show();
    });
  });
})();
