from api.infrastructure.models import generate_unique_code, Room
from django.contrib.auth.models import User
from django.db import IntegrityError

class RoomRepository:
    @staticmethod
    def get_by_code(code):
        return Room.objects.filter(code=code).first()

    @staticmethod
    def get_by_host(user):
        return Room.objects.filter(host=user).first()

    @staticmethod
    def create_or_update_room(host, guest_can_pause, votes_to_skip):
        room = Room.objects.filter(host=host).first()
        if room:
            # 更新現有房間
            room.guest_can_pause = guest_can_pause
            room.votes_to_skip = votes_to_skip
            room.save()
            return room, False
        else:
            # 新建房間，明確產生唯一 code，最多重試5次
            for _ in range(5):
                code = generate_unique_code()
                try:
                    room = Room.objects.create(
                        host=host,
                        guest_can_pause=guest_can_pause,
                        votes_to_skip=votes_to_skip,
                        code=code
                    )
                    return room, True
                except IntegrityError:
                    continue  # code 重複就重試
            raise IntegrityError("Failed to generate unique room code after several attempts.")

    @staticmethod
    def delete_by_code(code):
        room = Room.objects.filter(code=code).first()
        if room:
            room.delete()
        return room

    @staticmethod
    def delete_by_host(user):
        room = Room.objects.filter(host=user).first()
        if room:
            room.delete()
        return room 