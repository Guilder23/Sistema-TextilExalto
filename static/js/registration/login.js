const toggle = document.getElementById('togglePassword');
const campo = document.getElementById('password');

toggle.addEventListener('click', () => {
  const visible = campo.type === 'text';
  campo.type = visible ? 'password' : 'text';
  toggle.innerHTML = `<i class="bi bi-eye${visible ? '' : '-slash'}"></i>`;
  toggle.setAttribute('aria-label', visible ? 'Mostrar contraseña' : 'Ocultar contraseña');
  toggle.setAttribute('aria-pressed', String(!visible));
});
