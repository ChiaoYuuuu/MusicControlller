# music_controller/celery.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "music_controller.settings")

app = Celery("music_controller")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "fetch-top-50-daily": {
        "task": "spotify.tasks.fetch_and_store_top_50_task",
        "schedule": crontab(hour=1, minute=0),  
    },
}
