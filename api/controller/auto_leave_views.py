from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError, APIException
from api.infrastructure.serializers import *
from api.infrastructure.models import Room

class AutoLeave(APIView):
    permission_classes = [AllowAny]
    def post(self, request, format=None):
        input_serializer = AutoLeaveInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            raise ValidationError(input_serializer.errors)
        room_code = input_serializer.validated_data['room_code']
        room = Room.objects.filter(code=room_code).first()
        if room:
            room.delete()
            return Response({'message': 'Room deleted'}, status=200)
        else:
            return Response({'message': 'Room not found'}, status=404) 