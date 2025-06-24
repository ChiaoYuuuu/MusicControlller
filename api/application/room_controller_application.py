from api.domain.service.room_service import RoomService
from api.infrastructure.serializers import RoomSerializer, CreateRoomSerializer, UpdateRoomSerializer
from rest_framework import status
from django.http import JsonResponse
from django.core.cache import cache
from django.db import transaction

class RoomControllerService:
    @staticmethod
    def list_rooms():
        return RoomService.get_all_rooms()

    @staticmethod
    def get_room(user, code):
        data = RoomService.get_room_by_code(user, code)
        if data:
            return data, status.HTTP_200_OK
        return {'Room Not Found': 'Invalid Room Code.'}, status.HTTP_404_NOT_FOUND

    @staticmethod
    def join_room(user, code):
        room = RoomService.join_room(user, code)
        if room:
            return {'message': 'Room Joined!'}, status.HTTP_200_OK
        return {'Bad Request': 'Invalid Room Code'}, status.HTTP_400_BAD_REQUEST

    @staticmethod
    def create_room(user, guest_can_pause, votes_to_skip):
        room, created = RoomService.create_or_update_room(user, guest_can_pause, votes_to_skip)
        cache_key = f"user_room_{user.id}"
        cache.set(cache_key, room, timeout=600)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return RoomSerializer(room).data, status_code

    @staticmethod
    def user_in_room(user):
        code = RoomService.get_user_room(user)
        return {'code': code}, status.HTTP_200_OK

    @staticmethod
    def leave_room(user, room_code):
        cache_key = f"user_room_{user.id}"
        with transaction.atomic():
            result, message = RoomService.leave_room(user, room_code)
            cache.delete(cache_key)
            return {'message': message}, status.HTTP_200_OK if result else status.HTTP_404_NOT_FOUND

    @staticmethod
    def update_room(user, code, guest_can_pause, votes_to_skip):
        room = RoomService.join_room(user, code)
        if room:
            room.guest_can_pause = guest_can_pause
            room.votes_to_skip = votes_to_skip
            room.save()
            return RoomSerializer(room).data, status.HTTP_200_OK
        return {'Bad Request': 'Room not found'}, status.HTTP_404_NOT_FOUND 