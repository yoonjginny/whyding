from rest_framework import generics, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from django.utils import timezone
from drf_yasg import openapi
from .serializers import (
    SignupSerializer, 
    UserSerializer, 
    ChangePasswordSerializer, 
    DeleteAccountSerializer,
    LogoutSerializer
)
from .models import User
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView

class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_summary="회원가입",
        operation_description="새로운 사용자 계정을 생성합니다.",
        request_body=SignupSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="회원가입 성공",
                schema=UserSerializer
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="잘못된 요청",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'email': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                        'password': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                    }
                ),
                examples={
                    "application/json": {
                        "email": ["이미 존재하는 이메일입니다."],
                        "password": ["비밀번호가 일치하지 않습니다."]
                    }
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    @swagger_auto_schema(
        operation_summary="프로필 조회",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="프로필 조회 성공",
                schema=UserSerializer
            )
        }
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="프로필 수정",
        request_body=UserSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="프로필 수정 성공",
                schema=UserSerializer
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="잘못된 요청",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(type=openapi.TYPE_STRING, default="잘못된 요청입니다.")
                    }
                )
            )
        }
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
        request_body=ChangePasswordSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="비밀번호 변경 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING, default="비밀번호가 변경되었습니다.")
                    }
                )
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="비밀번호 변경 실패",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "old_password": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                        "detail": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def put(self, request, username):
        if request.user.username != username:
            return Response(
                {"detail": ("권한이 없습니다.")}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if not request.user.check_password(serializer.validated_data['old_password']):
            return Response(
                {"old_password": [("현재 비밀번호가 올바르지 않습니다.")]}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({"message": "비밀번호가 변경되었습니다."})

class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="계정 삭제",
        request_body=DeleteAccountSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="계정 삭제 성공",
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="계정 삭제 실패",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "password": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING))
                    }
                )
            )
        }
    )
    def delete(self, request):
        serializer = DeleteAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if not request.user.check_password(serializer.validated_data['password']):
            return Response(
                {"password": [("비밀번호가 올바르지 않습니다.")]}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TokenVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="토큰 검증",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="토큰 검증 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING, default="토큰이 유효합니다.")
                    }
                )
            )
        }
    )
    def get(self, request):
        return Response({"message": "토큰이 유효합니다."})

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    @swagger_auto_schema(
        operation_summary="로그아웃",
        request_body=LogoutSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="로그아웃 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING, default="로그아웃되었습니다.")
                    }
                ),
                examples={
                    "application/json": {
                        "message": "로그아웃되었습니다."
                    }
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="실패",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING, default="유효하지 않은 토큰입니다.")
                    }
                ),
                examples={
                    "application/json": {
                        "error": "유효하지 않은 토큰입니다."
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "로그아웃하려면 refresh_token이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh_token = serializer.validated_data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {"message": "로그아웃되었습니다."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"유효하지 않은 토큰입니다. 상세: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            try:
                User.objects.filter(email=request.data.get('email')).update(
                    last_login=timezone.now()
                )
                print(f"Last login updated for user: {request.data.get('email')}")
            except Exception as e:
                print(f"Error updating last_login: {str(e)}")
            
        return response