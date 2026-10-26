document.querySelectorAll('.alert-dismissible').forEach((alerta) => {
  setTimeout(() => bootstrap.Alert.getOrCreateInstance(alerta).close(), 6000);
});
