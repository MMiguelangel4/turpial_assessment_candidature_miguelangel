from django.apps import AppConfig


class BankConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bank"

    def ready(self) -> None:
        from . import signals  # noqa: F401  (registers the cached-balance signal)
