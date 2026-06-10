from django.apps import AppConfig


class ProgressConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "progress"

    def ready(self):
        # Import signals so they're registered when Django starts
        from . import signals  # noqa: F401
        