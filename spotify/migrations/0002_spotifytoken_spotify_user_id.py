# Generated by Django 4.2.20 on 2025-04-11 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("spotify", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="spotifytoken",
            name="spotify_user_id",
            field=models.CharField(blank=True, max_length=191, null=True, unique=True),
        ),
    ]
