const toggle = document.getElementById('togglePassword');
const campo = document.getElementById('password');
const formulario = document.getElementById('loginForm');

toggle?.addEventListener('click', () => {
  const visible = campo.type === 'text';
  campo.type = visible ? 'password' : 'text';
  toggle.innerHTML = `<i class="bi bi-eye${visible ? '' : '-slash'}"></i>`;
  toggle.setAttribute('aria-label', visible ? 'Mostrar contraseña' : 'Ocultar contraseña');
  toggle.setAttribute('aria-pressed', String(!visible));
});

formulario?.addEventListener('keydown', (event) => {
  if (event.key !== 'Enter' || event.target.tagName === 'TEXTAREA') {
    return;
  }

  if (event.target.id === 'username') {
    event.preventDefault();
    campo.focus();
  }
});
