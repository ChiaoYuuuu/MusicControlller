# spotify/infrastructure/serializers.py
from rest_framework import serializers

class CurrentSongInputSerializer(serializers.Serializer):
    room_code = serializers.CharField(required=True)

class CurrentSongOutputSerializer(serializers.Serializer):
    title = serializers.CharField()
    artist = serializers.CharField()
    duration = serializers.IntegerField()
    image_url = serializers.URLField()
    is_playing = serializers.BooleanField()
    skip_votes = serializers.IntegerField()
    votes_required = serializers.IntegerField()
    id = serializers.CharField()