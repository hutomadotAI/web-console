from django.apps import AppConfig


class Config(AppConfig):
    name = 'users'

    def ready(self):
        import users.signals  # noqa: F401
