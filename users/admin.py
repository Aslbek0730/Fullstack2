from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserPreference, LearningActivity

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'bio', 'profile_picture', 'date_of_birth')}),
        ('Learning preferences', {'fields': ('interests', 'learning_style')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'difficulty_preference', 'learning_pace', 'updated_at')
    search_fields = ('user__email', 'user__username')
    list_filter = ('difficulty_preference', 'learning_pace')

@admin.register(LearningActivity)
class LearningActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'content_type', 'content_id', 'created_at')
    search_fields = ('user__email', 'user__username', 'activity_type')
    list_filter = ('activity_type', 'content_type', 'created_at')

