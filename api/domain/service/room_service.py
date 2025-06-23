from api.repository.room_repository import RoomRepository
from api.infrastructure.serializers import RoomSerializer, CreateRoomSerializer, UpdateRoomSerializer
from api.infrastructure.models import Room

class RoomService:
    @staticmethod
    def join_room(user, code):
        room = RoomRepository.get_by_code(code)
        return room

    @staticmethod
    def create_or_update_room(user, guest_can_pause, votes_to_skip):
        room, created = RoomRepository.create_or_update_room(user, guest_can_pause, votes_to_skip)
        return room, created

    @staticmethod
    def leave_room(user, room_code):
        room = Room.objects.filter(code=room_code).first()
        if not room:
            return False, "Room not found"
        if room.host == user:
            room.delete()
            return True, "Host left, room deleted"
        else:
            return True, "User left, room still exists"

    @staticmethod
    def get_room_by_code(user, code):
        room = RoomRepository.get_by_code(code)
        if room:
            data = RoomSerializer(room).data
            data['is_host'] = user == room.host
            return data
        return None

    @staticmethod
    def get_user_room(user):
        room = RoomRepository.get_by_host(user)
        return room.code if room else None 