from django.apps import AppConfig


class HistorialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.historial'

    def ready(self):
        from . import signals  # noqa: F401
