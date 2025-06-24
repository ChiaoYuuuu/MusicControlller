from api.infrastructure.models import Room

def get_room(room_code):
    return Room.objects.filter(code=room_code).first() 