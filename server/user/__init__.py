from django.apps import AppConfig


class UserAppConfig(AppConfig):
    name = "user"

    def ready(self):
        from . import tasks
        tasks.set_up_hooks()
