from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
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
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password/<str:username>/', ChangePasswordView.as_view(), name='password'),
    path('delete/', DeleteAccountView.as_view(), name='delete-account'),
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
