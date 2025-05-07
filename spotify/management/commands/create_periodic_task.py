from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json

class Command(BaseCommand):
    help = 'Create periodic task to fetch Spotify Top 10 for multiple countries every 15 minutes'

    def handle(self, *args, **kwargs):
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=15,
            period=IntervalSchedule.MINUTES
        )

        task_name = "Fetch Spotify Top 10"
        task_path = "spotify.tasks.fetch_and_store_top10_task"

        if not PeriodicTask.objects.filter(name=task_name).exists():
            PeriodicTask.objects.create(
                interval=schedule,
                name=task_name,
                task=task_path,
                args=json.dumps([]),
            )
            self.stdout.write(self.style.SUCCESS(f"✅ PeriodicTask '{task_name}' created"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️ PeriodicTask '{task_name}' already exists"))
