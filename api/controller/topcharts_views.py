from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import APIException
from api.application.topcharts_application import TopChartsApplication
from api.infrastructure.serializers import *

class TopSong(APIView):
    permission_classes = [AllowAny]
    def get(self, request, format=None):
        data, error = TopChartsApplication.get_top_songs()
        if error:
            raise APIException(error)
        # 回傳所有國家資料，格式為 {country_code: [song, ...], ...}
        return Response(data) 