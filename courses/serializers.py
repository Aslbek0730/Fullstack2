from rest_framework import serializers
from .models import (
    Category, Course, Lesson, Quiz, Question, Answer,
    Enrollment, LessonProgress, QuizAttempt, QuizResponse
)

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for course categories.
    """
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'parent', 'icon')

class AnswerSerializer(serializers.ModelSerializer):
    """
    Serializer for quiz answers.
    """
    class Meta:
        model = Answer
        fields = ('id', 'answer_text', 'is_correct')
        extra_kwargs = {
            'is_correct': {'write_only': True}  # Hide correct answers from students
        }

class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for quiz questions.
    """
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ('id', 'question_text', 'question_type', 'points', 'order', 'answers')

class QuizSerializer(serializers.ModelSerializer):
    """
    Serializer for quizzes.
    """
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = ('id', 'title', 'description', 'time_limit', 'passing_score', 'questions')

class LessonSerializer(serializers.ModelSerializer):
    """
    Serializer for course lessons.
    """
    quizzes = QuizSerializer(many=True, read_only=True)
    
    class Meta:
        model = Lesson
        fields = ('id', 'title', 'slug', 'description', 'order', 'content', 
                  'video_url', 'duration', 'is_published', 'is_free_preview', 'quizzes')

class CourseListSerializer(serializers.ModelSerializer):
    """
    Serializer for course list view (limited details).
    """
    instructor_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    lesson_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Course
        fields = ('id', 'title', 'slug', 'short_description', 'thumbnail', 
                  'level', 'duration', 'instructor_name', 'category_name', 
                  'lesson_count', 'is_featured')
    
    def get_instructor_name(self, obj):
        return f"{obj.instructor.first_name} {obj.instructor.last_name}".strip() or obj.instructor.username
    
    def get_category_name(self, obj):
        return obj.category.name

class CourseDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for course detail view (full details).
    """
    lessons = LessonSerializer(many=True, read_only=True)
    instructor_name = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = Course
        fields = ('id', 'title', 'slug', 'description', 'short_description', 
                  'category', 'instructor', 'instructor_name', 'level', 
                  'duration', 'prerequisites', 'learning_objectives', 
                  'thumbnail', 'preview_video', 'lessons', 'created_at', 'updated_at')
    
    def get_instructor_name(self, obj):
        return f"{obj.instructor.first_name} {obj.instructor.last_name}".strip() or obj.instructor.username

class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Serializer for course enrollments.
    """
    course_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = ('id', 'course', 'course_title', 'status', 'progress', 
                  'enrolled_at', 'updated_at', 'completed_at')
        read_only_fields = ('progress', 'enrolled_at', 'updated_at', 'completed_at')
    
    def get_course_title(self, obj):
        return obj.course.title

class LessonProgressSerializer(serializers.ModelSerializer):
    """
    Serializer for tracking lesson progress.
    """
    lesson_title = serializers.SerializerMethodField()
    
    class Meta:
        model = LessonProgress
        fields = ('id', 'lesson', 'lesson_title', 'status', 'time_spent', 
                  'started_at', 'completed_at', 'last_accessed_at')
        read_only_fields = ('started_at', 'last_accessed_at')
    
    def get_lesson_title(self, obj):
        return obj.lesson.title

class QuizResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for quiz responses.
    """
    class Meta:
        model = QuizResponse
        fields = ('id', 'question', 'selected_answers', 'text_response', 
                  'score', 'is_correct', 'feedback')
        read_only_fields = ('score', 'is_correct', 'feedback')

class QuizAttemptSerializer(serializers.ModelSerializer):
    """
    Serializer for quiz attempts.
    """
    responses = QuizResponseSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = ('id', 'quiz', 'score', 'time_taken', 'is_completed', 
                  'started_at', 'completed_at', 'responses')
        read_only_fields = ('score', 'started_at', 'completed_at')

class QuizSubmissionSerializer(serializers.Serializer):
    """
    Serializer for submitting quiz answers.
    """
    quiz_id = serializers.IntegerField()
    time_taken = serializers.IntegerField()
    responses = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )

