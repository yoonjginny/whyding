from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Feedback
from .serializers import FeedbackSerializer
from drf_yasg.utils import swagger_auto_schema

# Create your views here.

class FeedbackCreateView(generics.CreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="피드백 작성",
        operation_description="서비스 이용 후 피드백을 작성합니다."
    )
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
