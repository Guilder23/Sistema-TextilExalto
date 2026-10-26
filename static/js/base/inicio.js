document.querySelectorAll('.stat-value').forEach((el) => {
  const meta = parseInt(el.textContent, 10);
  if (Number.isNaN(meta) || meta === 0) return;
  let actual = 0;
  const paso = Math.max(1, Math.ceil(meta / 20));
  const id = setInterval(() => {
    actual = Math.min(meta, actual + paso);
    el.textContent = actual;
    if (actual === meta) clearInterval(id);
  }, 30);
});
