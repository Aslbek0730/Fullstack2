from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ChatSessionViewSet, AIFeedbackViewSet, RecommendationViewSet,
    VoiceAssistantViewSet, AssessmentViewSet
)

router = DefaultRouter()
router.register(r'chat', ChatSessionViewSet, basename='chat')
router.register(r'feedback', AIFeedbackViewSet, basename='feedback')
router.register(r'recommendations', RecommendationViewSet, basename='recommendations')
router.register(r'voice', VoiceAssistantViewSet, basename='voice')
router.register(r'assessment', AssessmentViewSet, basename='assessment')

urlpatterns = [
    path('', include(router.urls)),
]

