from rest_framework import serializers

class LoginInputSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class LoginOutputSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

class RegisterInputSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class RegisterOutputSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

class TokenRefreshInputSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class TokenRefreshOutputSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField() 