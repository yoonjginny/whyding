from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import SignupSerializer, UserSerializer, ChangePasswordSerializer, DeleteAccountSerializer
from .models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate

class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"user": serializer.data}, status=status.HTTP_201_CREATED)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request, username):
        if request.user.username != username:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                email=request.user.email,
                password=serializer.validated_data['old_password']
            )
            if user:
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response({"message": "Password updated"}, status=status.HTTP_200_OK)
            else:
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        serializer = DeleteAccountSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                email=request.user.email,
                password=serializer.validated_data['password']
            )
            if user:
                user.delete()
                return Response({"message": "Account deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TokenVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 요청이 유효한 경우, 200 OK 응답을 반환
        return Response({"message": "Token is valid."}, status=status.HTTP_200_OK)