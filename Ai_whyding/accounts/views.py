from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import RegisterSerializer, UserSerializer, DeleteAccountSerializer
from .models import CustomUser
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.contrib.auth.hashers import make_password

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    회원가입 API

    사용자가 ID, 비밀번호, 이메일, 이름, 프로필 사진을 입력하여 회원가입을 할 수 있습니다.
    - **username**: 사용자 아이디 (필수)
    - **password**: 사용자 비밀번호 (필수)
    - **email**: 사용자 이메일 (필수)
    - **name**: 사용자 이름 (필수)
    - **profile Image**: 프로필 사진 (선택)

    성공적으로 회원가입이 완료되면 메시지를 반환합니다.
    """
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]  # 모든 사용자에게 접근 허용

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({"message": "회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)
    
    
class LoginView(generics.GenericAPIView):
    """
    사용자 로그인 API.
    
    사용자가 ID와 비밀번호를 입력하여 로그인을 할 수 있습니다.
    
    - **username**: 사용자 아이디
    - **password**: 사용자 비밀번호
    
    로그인에 성공하면 토큰과 함께 성공 메시지를 반환하고, 실패 시 오류 메시지를 반환합니다.
    """
    permission_classes = [AllowAny]  # 모든 사용자에게 접근 허용

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"message": "로그인이 성공했습니다.", "token": token.key}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "로그인에 실패했습니다. 사용자명 또는 비밀번호를 확인하세요."}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """
    사용자 로그아웃 API.
    
    인증된 사용자가 로그아웃을 요청할 수 있습니다.
    
    로그아웃에 성공하면 성공 메시지를 반환합니다.
    """
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "로그아웃 되었습니다."}, status=status.HTTP_200_OK)
    

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    사용자 프로필 조회 및 수정 API.
    
    인증된 사용자가 자신의 프로필 정보를 조회하거나 수정할 수 있습니다.
    
    - **GET** 요청: 자신의 프로필 정보를 조회합니다.
    - **PUT** 요청: 이메일, 이름, 프로필 사진을 수정할 수 있습니다.
    
    이메일 중복 검사를 수행하며, 수정된 이메일이 이미 존재하는 경우 오류 메시지를 반환합니다.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def get_object(self):
        username = self.kwargs.get('username')
        user = get_object_or_404(CustomUser, username=username)

        # 로그인한 사용자와 요청한 사용자가 같은지 확인
        if user != self.request.user:
            raise PermissionDenied("권한이 없습니다.")
        
        return user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # 이메일 중복 검사
        if 'email' in serializer.validated_data:
            email = serializer.validated_data['email']
            if CustomUser.objects.exclude(pk=user.pk).filter(email=email).exists():
                return Response({"email": "이메일이 이미 존재합니다."}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)
        return Response(serializer.data)
    

class ChangePasswordView(generics.UpdateAPIView):
    """
    비밀번호 변경 API

    인증된 사용자가 자신의 비밀번호를 변경할 수 있습니다.
    
    요청 데이터:
    - current_password: 현재 비밀번호 (필수)
    - new_password: 새로운 비밀번호 (필수)

    조건:
    - 현재 비밀번호가 올바르게 입력되어야 합니다.
    - 새 비밀번호는 현재 비밀번호와 달라야 합니다.
    - 새 비밀번호는 최소 8자 이상이어야 합니다.

    성공 시 비밀번호가 변경되고 성공 메시지를 반환합니다.
    실패 시 해당 오류 메시지를 반환합니다.
    """
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def put(self, request, *args, **kwargs):
        user = request.user
        username = kwargs.get('username')

        if user.username != username:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        # 기존 비밀번호 확인
        if not user.check_password(current_password):
            return Response({"message": "현재 비밀번호가 올바르지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 기존 비밀번호와 새 비밀번호가 같은지 확인
        if current_password == new_password:
            return Response({"message": "새로운 비밀번호는 기존 비밀번호와 달라야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 비밀번호 규칙 검증 (예시: 최소 8자)
        if len(new_password) < 8:
            raise ValidationError("비밀번호는 최소 8자 이상이어야 합니다.")

        # 새로운 비밀번호 해싱 후 저장
        user.password = make_password(new_password)
        user.save()

        return Response({"message": "비밀번호가 성공적으로 변경되었습니다."}, status=status.HTTP_200_OK)


class DeleteAccountView(APIView):
    """
    회원 탈퇴 API.

    로그인한 사용자가 비밀번호를 입력하여 자신의 계정을 삭제할 수 있습니다.

    계정 삭제가 완료되면 성공하였다는 메시지를 반환합니다.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = DeleteAccountSerializer

    def delete(self, request, username):
        # URL에서 전달된 username과 현재 로그인한 사용자의 username이 일치하는지 확인
        if request.user.username != username:
            return Response({"message": "자신의 계정만 삭제할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)

        user = get_object_or_404(User, username=username)
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            password = serializer.validated_data['password']
            if user.check_password(password):
                user.delete()
                return Response({"message": "계정이 성공적으로 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"message": "비밀번호가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
