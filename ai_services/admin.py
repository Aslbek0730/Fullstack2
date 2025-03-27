from django.contrib import admin
from .models import ChatSession, ChatMessage, UserEmbedding, CourseEmbedding, AIFeedback

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email', 'user__username', 'title')
    inlines = [ChatMessageInline]

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'role', 'content_preview', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('content', 'session__user__email')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

@admin.register(UserEmbedding)
class UserEmbeddingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('user__email', 'user__username')

@admin.register(CourseEmbedding)
class CourseEmbeddingAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('course__title',)

@admin.register(AIFeedback)
class AIFeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_type', 'content_id', 'score', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('user__email', 'feedback')

