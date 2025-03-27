from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, CourseViewSet, LessonViewSet,
    QuizViewSet, EnrollmentViewSet, LessonProgressViewSet,
    QuizAttemptViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'', CourseViewSet)

# Nested routes
lesson_router = DefaultRouter()
lesson_router.register(r'', LessonViewSet, basename='lesson')

quiz_router = DefaultRouter()
quiz_router.register(r'', QuizViewSet, basename='quiz')

enrollment_router = DefaultRouter()
enrollment_router.register(r'', EnrollmentViewSet, basename='enrollment')

progress_router = DefaultRouter()
progress_router.register(r'', LessonProgressViewSet, basename='progress')

quiz_attempt_router = DefaultRouter()
quiz_attempt_router.register(r'', QuizAttemptViewSet, basename='quiz-attempt')

urlpatterns = [
    path('', include(router.urls)),
    path('<slug:course_slug>/lessons/', include(lesson_router.urls)),
    path('lessons/<int:lesson_id>/quizzes/', include(quiz_router.urls)),
    path('enrollments/', include(enrollment_router.urls)),
    path('progress/', include(progress_router.urls)),
    path('quiz-attempts/', include(quiz_attempt_router.urls)),
]

