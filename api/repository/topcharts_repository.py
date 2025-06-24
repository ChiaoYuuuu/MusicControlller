from api.infrastructure.models import TopCharts
from django.utils import timezone
from datetime import timedelta

class TopChartsRepository:
    @staticmethod
    def get_latest_by_country_and_date(country_code, date):
        return TopCharts.objects.filter(country_code=country_code, retrieved_at__date=date).order_by('-retrieved_at').values_list('retrieved_at', flat=True).first()

    @staticmethod
    def get_songs_by_country_and_retrieved_at(country_code, retrieved_at, limit=10):
        return list(TopCharts.objects.filter(country_code=country_code, retrieved_at=retrieved_at).order_by('rank')[:limit].values('track_id', 'song_name', 'artist_name', 'rank'))

    @staticmethod
    def get_rank_map_by_country_and_retrieved_at(country_code, retrieved_at):
        return {
            song['track_id']: song['rank']
            for song in TopCharts.objects.filter(country_code=country_code, retrieved_at=retrieved_at).values('track_id', 'rank')
        } 