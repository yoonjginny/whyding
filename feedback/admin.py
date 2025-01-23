from django.contrib import admin
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'content', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'content']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    # 사용자별 피드백 수를 보여주는 필드 추가
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    # 상세 보기에서 보여줄 필드 구성
    fieldsets = (
        ('피드백 정보', {
            'fields': ('user', 'content', 'rating')
        }),
        ('시간 정보', {
            'fields': ('created_at',),
            'classes': ('collapse',)  # 접을 수 있는 섹션으로 만듦
        }),
    )
    
    # 사용자 권한에 따른 필드 제한
    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.readonly_fields + ['user', 'rating']
        return self.readonly_fields
