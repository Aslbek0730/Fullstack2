from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserPreference, LearningActivity

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'password_confirm', 
                  'first_name', 'last_name', 'bio', 'profile_picture', 
                  'date_of_birth', 'interests', 'learning_style')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }
    
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information.
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'bio', 'profile_picture', 
                  'date_of_birth', 'interests', 'learning_style')

class UserPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for user preferences.
    """
    class Meta:
        model = UserPreference
        fields = ('id', 'preferred_categories', 'difficulty_preference', 
                  'learning_pace', 'notification_settings')

class LearningActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for learning activities.
    """
    class Meta:
        model = LearningActivity
        fields = ('id', 'activity_type', 'content_type', 'content_id', 
                  'metadata', 'created_at')
        read_only_fields = ('created_at',)

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Comprehensive user profile serializer including preferences.
    """
    preferences = UserPreferenceSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 
                  'bio', 'profile_picture', 'date_of_birth', 
                  'interests', 'learning_style', 'preferences')
        read_only_fields = ('email', 'username')

