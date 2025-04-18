from django.db import models
from api.models import Room

class SpotifyToken(models.Model):
    user = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    refresh_token = models.CharField(max_length=150)
    access_token = models.CharField(max_length=150)
    expires_in = models.DateTimeField()
    token_type = models.CharField(max_length=50)
    spotify_user_id = models.CharField(max_length=191, unique=True, null=True, blank=True)

class SkipVote(models.Model):
    user = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    song_id = models.CharField(max_length=50)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    def __str__(self):
        return f"SkipVote - {self.user} / {self.song_id} / {self.room.code}"


class PreviousVote(models.Model):
    user = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    song_id = models.CharField(max_length=50)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('user', 'room', 'song_id') 
    def __str__(self):
        return f"PreviousVote - {self.user} / {self.song_id} / {self.room.code}"