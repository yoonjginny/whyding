from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import (
    SignupView,
    ProfileView,
    ChangePasswordView,
    DeleteAccountView,
    TokenVerifyView,
    LogoutView,
    CustomTokenObtainPairView,
    NaverLoginView,
    NaverCallbackView,
    KakaoLoginView,
    KakaoCallbackView,
    GoogleLoginView,
    GoogleCallbackView,
)
urlpatterns = [
    # 기존 URL 패턴
    path('signup/', SignupView.as_view(), name='signup'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password/<str:username>/', ChangePasswordView.as_view(), name='password'),
    path('delete/', DeleteAccountView.as_view(), name='delete-account'),
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # 소셜 로그인 URL 패턴
    path('naver/login/', NaverLoginView.as_view(), name='naver-login'),
    path('naver/callback/', NaverCallbackView.as_view(), name='naver-callback'),
    path('kakao/login/', KakaoLoginView.as_view(), name='kakao-login'),
    path('kakao/callback/', KakaoCallbackView.as_view(), name='kakao-callback'),
    path('google/login/', GoogleLoginView.as_view(), name='google-login'),
    path('google/callback/', GoogleCallbackView.as_view(), name='google-callback'),
]