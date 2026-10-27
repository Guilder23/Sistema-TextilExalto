document.querySelectorAll('.report-tabs .nav-link').forEach((tab) => {
  tab.addEventListener('click', () => document.body.classList.add('loading'));
});
