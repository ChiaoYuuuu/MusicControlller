from rest_framework import serializers

class TopSongOutputSerializer(serializers.Serializer):
    song_name = serializers.CharField()
    artist = serializers.CharField()
    # 根據 TopChartsService.get_top_songs() 實際回傳格式補充欄位 