# Generated by Django 4.2.21 on 2025-05-10 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spotify', '0007_alter_spotifytoken_access_token_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spotifytoken',
            name='access_token',
            field=models.CharField(max_length=300),
        ),
        migrations.AlterField(
            model_name='spotifytoken',
            name='refresh_token',
            field=models.CharField(max_length=300),
        ),
    ]
