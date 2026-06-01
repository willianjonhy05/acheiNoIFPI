from django.apps import AppConfig


class AcheinoifpiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'acheinoifpi'

    def ready(self):
        import acheinoifpi.signals