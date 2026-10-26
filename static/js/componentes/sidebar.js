(() => {
  const sidebar = document.getElementById('appSidebar');
  const backdrop = document.getElementById('sidebarBackdrop');
  const boton = document.getElementById('btnSidebar');
  if (!sidebar || !backdrop || !boton) return;

  const alternar = (abrir) => {
    sidebar.classList.toggle('open', abrir);
    backdrop.classList.toggle('show', abrir);
  };
  boton.addEventListener('click', () => alternar(!sidebar.classList.contains('open')));
  backdrop.addEventListener('click', () => alternar(false));
})();
