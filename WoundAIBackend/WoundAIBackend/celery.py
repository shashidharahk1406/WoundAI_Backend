import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WoundAIBackend.settings")

app = Celery("WoundAIBackend")

# Use Redis as broker
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all apps
app.autodiscover_tasks()
