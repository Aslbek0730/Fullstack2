from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import UserViewSet, UserPreferenceViewSet, LearningActivityViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')
router.register(r'preferences', UserPreferenceViewSet, basename='user-preference')
router.register(r'activities', LearningActivityViewSet, basename='learning-activity')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

