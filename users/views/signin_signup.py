from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User
from users.serializers import RegisterSerializer, LoginSerializer
from drf_yasg.utils import swagger_auto_schema


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class SignupView(APIView):
    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            return Response({'token': tokens['access'], **tokens}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SigninView(APIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        email_or_username = request.data.get('email_or_username')
        password = request.data.get('password')

        user = authenticate(username=email_or_username, password=password)

        if user is not None:
            tokens = get_tokens_for_user(user)
            return Response({'token': tokens['access'], **tokens}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

signup_view = SignupView.as_view()
signin_view = SigninView.as_view()
