from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction
from rest_framework.exceptions import ValidationError, APIException
from api.application.auth_application import AuthApplication, MyTokenObtainPairView
from api.infrastructure.serializers import *

class TokenRefresh(APIView):
    def post(self, request):
        input_serializer = TokenRefreshInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            raise ValidationError(input_serializer.errors)
        data, error = AuthApplication.refresh_token(input_serializer.validated_data['refresh'])
        if error:
            raise ValidationError(error)
        output_serializer = TokenRefreshOutputSerializer(data=data)
        if not output_serializer.is_valid():
            raise APIException('Internal server error: invalid response format.')
        return Response(output_serializer.data, status=status.HTTP_200_OK)

class Login(APIView):
    def post(self, request):
        input_serializer = LoginInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            raise ValidationError(input_serializer.errors)
        data, error = AuthApplication.login(**input_serializer.validated_data)
        if error:
            raise ValidationError(error)
        output_serializer = LoginOutputSerializer(data=data)
        if not output_serializer.is_valid():
            raise APIException('Internal server error: invalid response format.')
        return Response(output_serializer.data, status=status.HTTP_200_OK)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    @transaction.atomic
    def post(self, request):
        input_serializer = RegisterInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            raise ValidationError(input_serializer.errors)
        data, error = AuthApplication.register(**input_serializer.validated_data)
        if error:
            raise ValidationError(error)
        output_serializer = RegisterOutputSerializer(data=data)
        if not output_serializer.is_valid():
            raise APIException('Internal server error: invalid response format.')
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

class MyTokenObtainPairViewProxy(MyTokenObtainPairView):
    pass 