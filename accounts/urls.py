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
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password/<str:username>/', ChangePasswordView.as_view(), name='password'),
    path('delete/', DeleteAccountView.as_view(), name='delete-account'),
]
