from api.domain.service.auth_service import AuthService as DomainAuthService
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import IntegrityError

class AuthApplication:
    @staticmethod
    def login(username, password):
        _, error = DomainAuthService.validate_login(username, password)
        if error:
            return None, error
        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'username': user.username
            }, None
        else:
            return None, 'Invalid credentials'

    @staticmethod
    def register(username, password):
        _, error = DomainAuthService.validate_register(username, password)
        if error:
            return None, error
        try:
            user = User.objects.create_user(username=username, password=password)
            refresh = RefreshToken.for_user(user)
            return {
                "message": "User registered successfully",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }, None
        except IntegrityError:
            return None, 'Username already exists'
        except Exception:
            return None, 'Internal server error'

    @staticmethod
    def refresh_token(refresh_token):
        if not refresh_token:
            return None, 'Refresh token is required'
        try:
            refresh = RefreshToken(refresh_token)
            new_access = str(refresh.access_token)
            return {"access": new_access, "refresh": str(refresh)}, None
        except TokenError:
            return None, 'Invalid refresh token'

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username 
        token['user_id'] = user.id
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer 