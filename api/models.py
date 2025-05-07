from django.db import models
import random
import string
from django.contrib.auth.models import User

def generate_unique_code():
    length = 6

    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=length))
        if Room.objects.filter(code = code).count() == 0:
            break
    return code

from django.db import models

class TopCharts(models.Model):
    id = models.AutoField(primary_key=True)
    country_code = models.CharField(max_length=2)
    rank = models.IntegerField()
    track_id = models.CharField(max_length=255, default='temp-id')
    artist_name = models.CharField(max_length=255)
    song_name = models.CharField(max_length=255)
    spotify_url = models.CharField(max_length=500)
    retrieved_at = models.DateTimeField()

    class Meta:
        db_table = "top_charts"  
        managed = False
        app_label = 'api'

class Room(models.Model):
    code = models.CharField(max_length = 8, unique = True, default = generate_unique_code)
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    guest_can_pause = models.BooleanField(null=False, default=False)
    votes_to_skip = models.IntegerField(null=False, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    current_song = models.CharField(max_length=50, null=True)


