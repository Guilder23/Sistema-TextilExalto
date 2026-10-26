// Las acciones de cada fila las gestionan los scripts de cada modal (crear, editar, ver, eliminar).
// Aquí solo se expone la fila seleccionada para que los modales la reutilicen.
window.filaDeBoton = (boton) => boton.closest('tr');
