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
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('api/articles/', include('articles.urls')),
        path('api/accounts/', include('accounts.urls')),
    ],
)

def test_view(request):
    try:
        # 더 자세한 응답 반환
        return HttpResponse(
            f"Server is running!\nHost: {request.get_host()}\nPath: {request.path}",
            status=200
        )
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)

urlpatterns = [
    path('', test_view),  # 맨 위로 이동
    path('admin/', admin.site.urls),
    path('api/articles/', include('articles.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api/feedback/', include('feedback.urls')),
    
    # Swagger URL
    path('api/swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/accounts/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

