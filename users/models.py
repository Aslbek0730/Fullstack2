from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    """
    email = models.EmailField(_('email address'), unique=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Learning preferences
    interests = models.JSONField(default=list, blank=True)
    learning_style = models.CharField(max_length=50, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Make email the required field for login instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        
    def __str__(self):
        return self.email

class UserPreference(models.Model):
    """
    User preferences for personalization and recommendations.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    preferred_categories = models.JSONField(default=list, blank=True)
    difficulty_preference = models.CharField(max_length=20, blank=True)
    learning_pace = models.CharField(max_length=20, blank=True)
    notification_settings = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email}'s preferences"

class LearningActivity(models.Model):
    """
    Tracks user learning activities for analytics and recommendations.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_activities')
    activity_type = models.CharField(max_length=50)  # e.g., 'course_view', 'lesson_complete', 'quiz_attempt'
    content_type = models.CharField(max_length=50)  # e.g., 'course', 'lesson', 'quiz'
    content_id = models.IntegerField()
    metadata = models.JSONField(default=dict, blank=True)  # Additional data about the activity
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['user', 'content_type', 'content_id']),
            models.Index(fields=['created_at']),
        ]
        
    def __str__(self):
        return f"{self.user.email} - {self.activity_type} - {self.created_at}"

