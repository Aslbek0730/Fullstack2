from rest_framework import serializers
from .models import ChatSession, ChatMessage, AIFeedback

class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for chat messages.
    """
    class Meta:
        model = ChatMessage
        fields = ('id', 'role', 'content', 'created_at')
        read_only_fields = ('created_at',)

class ChatSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for chat sessions.
    """
    messages = ChatMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatSession
        fields = ('id', 'title', 'created_at', 'updated_at', 'messages')
        read_only_fields = ('created_at', 'updated_at')

class ChatMessageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new chat messages.
    """
    class Meta:
        model = ChatMessage
        fields = ('content',)

class AIFeedbackSerializer(serializers.ModelSerializer):
    """
    Serializer for AI feedback.
    """
    class Meta:
        model = AIFeedback
        fields = ('id', 'content_type', 'content_id', 'feedback', 'score', 'created_at')
        read_only_fields = ('created_at',)

class CourseRecommendationRequestSerializer(serializers.Serializer):
    """
    Serializer for course recommendation requests.
    """
    count = serializers.IntegerField(default=5, min_value=1, max_value=20)
    include_enrolled = serializers.BooleanField(default=False)

class EssayGradingRequestSerializer(serializers.Serializer):
    """
    Serializer for essay grading requests.
    """
    essay_text = serializers.CharField(required=True)
    rubric = serializers.CharField(required=False)
    max_score = serializers.IntegerField(default=100, min_value=1)

class VoiceCommandSerializer(serializers.Serializer):
    """
    Serializer for voice command requests.
    """
    text = serializers.CharField(required=False)
    # audio file is handled directly in the view

class TextToSpeechSerializer(serializers.Serializer):
    """
    Serializer for text-to-speech requests.
    """
    text = serializers.CharField(required=True)
    language = serializers.CharField(required=False, default='en')

class LessonAudioSerializer(serializers.Serializer):
    """
    Serializer for lesson audio requests.
    """
    lesson_id = serializers.IntegerField(required=True)
    language = serializers.CharField(required=False, default='en')

class StudyPlanRequestSerializer(serializers.Serializer):
    """
    Serializer for study plan requests.
    """
    course_id = serializers.IntegerField(required=False)
    target_date = serializers.DateField(required=False)

