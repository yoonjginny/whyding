from django.urls import path
from .views import RegisterView, LoginView, LogoutView, UserProfileView, ChangePasswordView, DeleteAccountView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('signup/', RegisterView.as_view(), name='signup'),  # 회원가입
    path('login/', LoginView.as_view(), name='login'),  # 로그인
    path('logout/', LogoutView.as_view(), name='logout'),  # 로그아웃
    path('<str:username>/', UserProfileView.as_view(), name='user-profile'), # 프로필 조회 및 수정
    path('password/<str:username>/', ChangePasswordView.as_view(), name='password'),  # 비밀번호 변경
    path('delete-account/<str:username>/', DeleteAccountView.as_view(), name='delete-account'), #회원탈퇴
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
