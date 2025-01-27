from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from django.utils import timezone
from drf_yasg import openapi
from django.conf import settings
import requests
import jwt
from datetime import datetime, timedelta
from .serializers import (
    SignupSerializer, 
    UserSerializer, 
    ChangePasswordSerializer, 
    DeleteAccountSerializer,
    LogoutSerializer
)
from .models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from urllib.parse import quote

class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = []
    
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
    
    def get_serializer_context(self):
        return {'request': self.request}

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
        serializer = UserSerializer(
            request.user,
            context=self.get_serializer_context()  # context 추가
        )
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
        serializer = UserSerializer(
            request.user, 
            data=request.data, 
            partial=True,
            context=self.get_serializer_context()  # context 추가
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

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
                {"detail": "권한이 없습니다."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if not request.user.check_password(serializer.validated_data['old_password']):
            return Response(
                {"old_password": ["현재 비밀번호가 올바르지 않습니다."]}, 
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
    
class NaverLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        client_id = settings.NAVER_CLIENT_ID
        redirect_uri = settings.NAVER_REDIRECT_URI

        naver_auth_url = f"https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&state=STATE_STRING"

        return Response({
            "message": "네이버 로그인 URL입니다.",
            "url": naver_auth_url
        }, status=status.HTTP_200_OK)

class NaverCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')

        if not code:
            return Response({
                "message": "인증 코드가 없습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        token_request = requests.get(
            f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={settings.NAVER_CLIENT_ID}&client_secret={settings.NAVER_CLIENT_SECRET}&code={code}&state={state}"
        )
        token_response = token_request.json()

        access_token = token_response.get('access_token')

        if not access_token:
            return Response({
                "message": "액세스 토큰을 받아오는데 실패했습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        profile_request = requests.get(
            "https://openapi.naver.com/v1/nid/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        profile_response = profile_request.json()

        if profile_response.get('resultcode') != '00':
            return Response({
                "message": "사용자 정보를 가져오는데 실패했습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        naver_account = profile_response.get('response')
        if not naver_account:
            return Response({
                "message": "네이버 계정 정보를 가져오는데 실패했습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        social_id = naver_account.get('id')
        email = naver_account.get('email')
        name = naver_account.get('name')

        if not social_id or not email or not name:
            return Response({
                "message": "필수 사용자 정보가 누락되었습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(social_id=social_id)
            user.username = name
            user.save()
        except User.DoesNotExist:
            user = User.objects.create(
                username=name,
                email=email,
                social_id=social_id,
                provider='naver'
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "네이버 로그인 성공",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data
        }, status=status.HTTP_200_OK)

class KakaoLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        client_id = settings.KAKAO_CLIENT_ID
        redirect_uri = settings.KAKAO_REDIRECT_URI

        kakao_auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"

        return Response({
            "message": "카카오 로그인 URL입니다.",
            "url": kakao_auth_url
        }, status=status.HTTP_200_OK)

class KakaoCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get('code')

        if not code:
            return Response({
                "message": "인증 코드가 없습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        token_request = requests.post(
            "https://kauth.kakao.com/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": settings.KAKAO_CLIENT_ID,
                "redirect_uri": settings.KAKAO_REDIRECT_URI,
                "code": code
            }
        )
        token_response = token_request.json()

        access_token = token_response.get('access_token')

        if not access_token:
            return Response({
                "message": "액세스 토큰을 받아오는데 실패했습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        profile_request = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"property_keys": '["properties.nickname", "kakao_account.email"]'}
        )
        profile_response = profile_request.json()

        if 'id' not in profile_response:
            return Response({
                "message": "사용자 정보를 가져오는데 실패했습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        properties = profile_response.get('properties', {})
        kakao_account = profile_response.get('kakao_account', {})

        kakao_id = str(profile_response.get('id'))
        nickname = properties.get('nickname')
        email = kakao_account.get('email')

        if not nickname:
            return Response({
                "message": "닉네임 정보 제공에 동의해주세요."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(social_id=kakao_id)
            user.username = nickname
            if email and kakao_account.get('is_email_valid') and kakao_account.get('is_email_verified'):
                user.email = email
            user.save()
        except User.DoesNotExist:
            username = nickname or f"kakao_{kakao_id}"
            email_to_use = email if (email and kakao_account.get('is_email_valid') and kakao_account.get('is_email_verified')) else f"{kakao_id}@kakao.user"
            user = User.objects.create(
                username=username,
                email=email_to_use,
                social_id=kakao_id,
                provider='kakao'
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "카카오 로그인 성공",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data
        }, status=status.HTTP_200_OK)

class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        client_id = settings.GOOGLE_CLIENT_ID
        redirect_uri = settings.GOOGLE_REDIRECT_URI

        scope = "email profile openid https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email"
        encoded_scope = quote(scope)

        google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={encoded_scope}&access_type=offline"

        return Response({
            "message": "구글 로그인 URL입니다.",
            "url": google_auth_url
        }, status=status.HTTP_200_OK)

class GoogleCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get('code')

        if not code:
            return Response({
                "message": "인증 코드가 없습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        token_request = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code"
            }
        )
        token_response = token_request.json()

        access_token = token_response.get('access_token')

        if not access_token:
            return Response({
                "message": "액세스 토큰을 받아오는데 실패했습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        profile_request = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        profile_response = profile_request.json()

        # print("Google Profile Response (v3):", profile_response)  # 상세 로그 추가

        if 'sub' not in profile_response:
            return Response({
                "message": "사용자 정보를 가져오는데 실패했습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        google_id = profile_response.get('sub')
        email = profile_response.get('email')
        name = profile_response.get('name', '')

        try:
            user = User.objects.get(social_id=google_id)
            user.username = name or f"google_{google_id}"
            if email:
                user.email = email
            user.save()
        except User.DoesNotExist:
            user = User.objects.create(
                username=name or f"google_{google_id}",
                email=email or f"{google_id}@google.user",
                social_id=google_id,
                provider='google'
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "구글 로그인 성공",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data
        }, status=status.HTTP_200_OK)