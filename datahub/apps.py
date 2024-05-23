from django.apps import AppConfig


class DatahubConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "datahub"

    def ready(self):
        import combo_investment.celery

        # import datahub.tasks
