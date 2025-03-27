from rest_framework import viewsets, generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .models import UserPreference, LearningActivity
from .serializers import (
    UserSerializer, UserUpdateSerializer, UserPreferenceSerializer,
    LearningActivitySerializer, UserProfileSerializer
)

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user management.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()
    
    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer
        elif self.action == 'me':
            return UserProfileSerializer
        return self.serializer_class
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """
        Get or update the current user's profile.
        """
        user = request.user
        
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        
        serializer = UserUpdateSerializer(user, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPreferenceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user preferences.
    """
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserPreference.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class LearningActivityViewSet(viewsets.ModelViewSet):
    """
    API endpoint for tracking learning activities.
    """
    serializer_class = LearningActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return LearningActivity.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get learning activity statistics for the current user.
        """
        user = request.user
        activities = LearningActivity.objects.filter(user=user)
        
        # Calculate basic statistics
        total_activities = activities.count()
        activity_types = activities.values('activity_type').distinct().count()
        
        # Get recent activities
        recent = activities.order_by('-created_at')[:5]
        recent_serializer = self.get_serializer(recent, many=True)
        
        return Response({
            'total_activities': total_activities,
            'activity_types': activity_types,
            'recent_activities': recent_serializer.data
        })

