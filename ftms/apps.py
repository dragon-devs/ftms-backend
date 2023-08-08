from django.apps import AppConfig


class FtmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ftms'

    def ready(self):
        import ftms.signals
