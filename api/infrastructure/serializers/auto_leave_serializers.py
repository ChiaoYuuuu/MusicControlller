from rest_framework import serializers

class AutoLeaveInputSerializer(serializers.Serializer):
    room_code = serializers.CharField()

class AutoLeaveOutputSerializer(serializers.Serializer):
    message = serializers.CharField() 