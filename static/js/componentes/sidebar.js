(() => {
  const sidebar = document.getElementById('appSidebar');
  const backdrop = document.getElementById('sidebarBackdrop');
  const boton = document.getElementById('btnSidebar');
  if (!sidebar || !backdrop || !boton) return;

  const escritorio = () => window.matchMedia('(min-width: 992px)').matches;
  const actualizar = () => {
    const colapsado = document.body.classList.contains('sidebar-collapsed');
    boton.setAttribute('aria-expanded', String(!colapsado));
    boton.setAttribute('aria-label', colapsado ? 'Expandir menú' : 'Contraer menú');
  };
  const alternar = () => {
    if (escritorio()) {
      document.body.classList.toggle('sidebar-collapsed');
      localStorage.setItem('sidebar-collapsed', document.body.classList.contains('sidebar-collapsed'));
      actualizar();
      return;
    }
    const abrir = !sidebar.classList.contains('open');
    sidebar.classList.toggle('open', abrir);
    backdrop.classList.toggle('show', abrir);
  };
  if (escritorio() && localStorage.getItem('sidebar-collapsed') === 'true') {
    document.body.classList.add('sidebar-collapsed');
  }
  actualizar();
  boton.addEventListener('click', alternar);
  backdrop.addEventListener('click', () => {
    sidebar.classList.remove('open');
    backdrop.classList.remove('show');
  });
  window.addEventListener('resize', actualizar);
})();
