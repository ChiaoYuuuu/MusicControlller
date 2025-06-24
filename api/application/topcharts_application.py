from django.utils import timezone
from api.domain.service.topcharts_service import TopChartsService

class TopChartsApplication:
    @staticmethod
    def get_top_songs():
        today = timezone.now().date()
        return TopChartsService.get_top_songs(today)