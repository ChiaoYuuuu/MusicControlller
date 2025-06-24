# project_root/celery.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_root.settings")

app = Celery("project_root")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "fetch-top-50-daily": {
        "task": "spotify.management.commands.create_periodic_task.fetch_and_store_top10_task",
        "schedule": crontab(hour=19, minute=10),  
    },
}
