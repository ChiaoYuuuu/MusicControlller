from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied, APIException
from api.application.room_controller_application import RoomControllerService
from api.infrastructure.serializers import *

class RoomView(generics.ListAPIView):
    serializer_class = RoomSerializer
    def get_queryset(self):
        return RoomControllerService.list_rooms()

class GetRoom(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        input_serializer = GetRoomInputSerializer(data=request.GET)
        if not input_serializer.is_valid():
            raise ValidationError(input_serializer.errors)
        code = input_serializer.validated_data['code']
        data, status_code = RoomControllerService.get_room(request.user, code)
        if status_code == status.HTTP_200_OK:
            output_serializer = GetRoomOutputSerializer(data=data)
            if not output_serializer.is_valid():
                raise APIException('Internal server error: invalid response format.')
            return Response(output_serializer.data, status=status_code)
        elif status_code == status.HTTP_404_NOT_FOUND:
            raise NotFound(data)
        elif status_code == status.HTTP_403_FORBIDDEN:
            raise PermissionDenied(data)
        else:
            raise APIException(data)

class JoinRoom(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        input_serializer = JoinRoomInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            raise ValidationError(input_serializer.errors)
        code = input_serializer.validated_data['code']
        data, status_code = RoomControllerService.join_room(request.user, code)
        if status_code == status.HTTP_404_NOT_FOUND:
            raise NotFound(data)
        elif status_code == status.HTTP_403_FORBIDDEN:
            raise PermissionDenied(data)
        output_serializer = JoinRoomOutputSerializer(data=data)
        if not output_serializer.is_valid():
            raise APIException('Internal server error: invalid response format.')
        return Response(output_serializer.data, status=status_code)

class CreateRoomView(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request, format=None):
        input_serializer = CreateRoomInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            raise ValidationError(input_serializer.errors)
        guest_can_pause = input_serializer.validated_data['guest_can_pause']
        votes_to_skip = input_serializer.validated_data['votes_to_skip']
        data, status_code = RoomControllerService.create_room(request.user, guest_can_pause, votes_to_skip)
        output_serializer = CreateRoomOutputSerializer(data=data)
        if not output_serializer.is_valid():
            raise APIException(f'Internal server error: invalid response format. {output_serializer.errors}')
        return Response(output_serializer.data, status=status_code)

class UserInRoom(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        data, status_code = RoomControllerService.user_in_room(request.user)
        output_serializer = UserInRoomOutputSerializer(data=data)
        if not output_serializer.is_valid():
            raise APIException('Internal server error: invalid response format.')
        return Response(output_serializer.data, status=status_code)

class LeaveRoom(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request, format=None):
        room_code = request.data.get('room_code')
        if not room_code:
            return Response({'message': 'Room code is required'}, status=400)
        success, message = RoomControllerService.leave_room(request.user, room_code)
        if not success:
            return Response({'message': message}, status=404)
        return Response({'message': message}, status=200)

class UpdateRoom(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, format=None):
        input_serializer = UpdateRoomInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            raise ValidationError(input_serializer.errors)
        code = input_serializer.validated_data['code']
        guest_can_pause = input_serializer.validated_data['guest_can_pause']
        votes_to_skip = input_serializer.validated_data['votes_to_skip']
        data, status_code = RoomControllerService.update_room(request.user, code, guest_can_pause, votes_to_skip)
        if status_code == status.HTTP_404_NOT_FOUND:
            raise NotFound(data)
        elif status_code == status.HTTP_403_FORBIDDEN:
            raise PermissionDenied(data)
        elif status_code == status.HTTP_200_OK:
            output_serializer = UpdateRoomOutputSerializer(data=data)
            if not output_serializer.is_valid():
                raise APIException('Internal server error: invalid response format.')
            return Response(output_serializer.data, status=status_code)
        else:
            raise APIException(data) 