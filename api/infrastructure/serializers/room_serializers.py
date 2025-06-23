from rest_framework import serializers
from api.infrastructure.models import Room

class RoomSerializer(serializers.ModelSerializer):
    host = serializers.StringRelatedField()
    class Meta:
        model = Room
        fields = ('id', 'code', 'host', 'guest_can_pause', 'votes_to_skip', 'created_at')

class CreateRoomInputSerializer(serializers.Serializer):
    guest_can_pause = serializers.BooleanField()
    votes_to_skip = serializers.IntegerField(min_value=1)
    def validate_votes_to_skip(self, value):
        if value < 1:
            raise serializers.ValidationError("votes_to_skip 必須大於 0")
        return value

class CreateRoomOutputSerializer(RoomSerializer):
    pass

class UpdateRoomInputSerializer(serializers.Serializer):
    code = serializers.CharField()
    guest_can_pause = serializers.BooleanField()
    votes_to_skip = serializers.IntegerField(min_value=1)
    def validate_votes_to_skip(self, value):
        if value < 1:
            raise serializers.ValidationError("votes_to_skip 必須大於 0")
        return value

class UpdateRoomOutputSerializer(RoomSerializer):
    pass

class JoinRoomInputSerializer(serializers.Serializer):
    code = serializers.CharField()

class JoinRoomOutputSerializer(serializers.Serializer):
    message = serializers.CharField()

class LeaveRoomOutputSerializer(serializers.Serializer):
    message = serializers.CharField()

class UserInRoomOutputSerializer(serializers.Serializer):
    code = serializers.CharField(allow_null=True)

class GetRoomInputSerializer(serializers.Serializer):
    code = serializers.CharField()

class GetRoomOutputSerializer(RoomSerializer):
    is_host = serializers.BooleanField()
    class Meta(RoomSerializer.Meta):
        fields = RoomSerializer.Meta.fields + ('is_host',)
        
# 保留原有 CreateRoomSerializer, UpdateRoomSerializer 以相容舊程式
class CreateRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('guest_can_pause', 'votes_to_skip')

class UpdateRoomSerializer(serializers.ModelSerializer):
    code = serializers.CharField(validators = [])
    class Meta:
        model = Room
        fields = ('guest_can_pause', 'votes_to_skip', 'code') 