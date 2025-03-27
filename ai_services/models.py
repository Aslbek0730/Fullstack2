from django.db import models
from django.conf import settings

class ChatSession(models.Model):
    """
    Stores chat sessions between users and the AI assistant.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Chat session {self.id} - {self.user.email}"

class ChatMessage(models.Model):
    """
    Stores individual messages in a chat session.
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."

class UserEmbedding(models.Model):
    """
    Stores user embeddings for recommendation system.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='embedding')
    embedding_vector = models.BinaryField()  # Stored as pickled numpy array
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Embedding for {self.user.email}"

class CourseEmbedding(models.Model):
    """
    Stores course embeddings for recommendation system.
    """
    course = models.OneToOneField('courses.Course', on_delete=models.CASCADE, related_name='embedding')
    embedding_vector = models.BinaryField()  # Stored as pickled numpy array
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Embedding for {self.course.title}"

class AIFeedback(models.Model):
    """
    Stores AI-generated feedback on user submissions.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_feedback')
    content_type = models.CharField(max_length=50)  # e.g., 'quiz_response', 'assignment'
    content_id = models.IntegerField()
    feedback = models.TextField()
    score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"AI Feedback for {self.user.email} - {self.content_type} {self.content_id}"

