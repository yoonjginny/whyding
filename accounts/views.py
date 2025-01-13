from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from .serializers import (
    SignupSerializer, 
    UserSerializer, 
    ChangePasswordSerializer, 
    DeleteAccountSerializer
)
from .models import User

class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_summary="회원가입",
        operation_description="새로운 사용자 계정을 생성합니다."
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="프로필 조회",
        responses={200: UserSerializer}
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="프로필 수정",
        request_body=UserSerializer,
        responses={200: UserSerializer}
    )
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="비밀번호 변경",
        request_body=ChangePasswordSerializer
    )
    def put(self, request, username):
        if request.user.username != username:
            return Response(
                {"detail": _("권한이 없습니다.")}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if not request.user.check_password(serializer.validated_data['old_password']):
            return Response(
                {"old_password": [_("현재 비밀번호가 올바르지 않습니다.")]}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({"message": _("비밀번호가 변경되었습니다.")})

class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="계정 삭제",
        request_body=DeleteAccountSerializer
    )
    def delete(self, request):
        serializer = DeleteAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if not request.user.check_password(serializer.validated_data['password']):
            return Response(
                {"password": [_("비밀번호가 올바르지 않습니다.")]}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TokenVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="토큰 검증",
        responses={200: {"message": "Token is valid."}}
    )
    def get(self, request):
        return Response({"message": _("토큰이 유효합니다.")})

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="로그아웃",
        request_body=serializers.Serializer({"refresh_token": serializers.CharField()})
    )
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": _("로그아웃되었습니다.")})
        except Exception:
            return Response(
                {"error": _("유효하지 않은 토큰입니다.")}, 
                status=status.HTTP_400_BAD_REQUEST
            )