from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from accounts.views import CustomTokenObtainPairView
from django.http import HttpResponse

schema_view = get_schema_view(
    openapi.Info(
        title="API 문서",
        default_version='v1',
        description="API 설명",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

def health_check(request):
    return HttpResponse("OK")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/articles/', include('articles.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api/feedback/', include('feedback.urls')),
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/accounts/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('health/', health_check, name='health_check'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

