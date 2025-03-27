from rest_framework import viewsets, generics, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Category, Course, Lesson, Quiz, Question, Answer,
    Enrollment, LessonProgress, QuizAttempt, QuizResponse
)
from .serializers import (
    CategorySerializer, CourseListSerializer, CourseDetailSerializer,
    LessonSerializer, QuizSerializer, QuestionSerializer,
    EnrollmentSerializer, LessonProgressSerializer,
    QuizAttemptSerializer, QuizSubmissionSerializer
)
from .permissions import IsInstructorOrReadOnly, IsEnrolledOrInstructor
from ai_services.tasks import grade_essay_response

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for course categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'

class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for courses.
    """
    queryset = Course.objects.annotate(lesson_count=Count('lessons'))
    serializer_class = CourseListSerializer
    permission_classes = [IsInstructorOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'level', 'is_featured']
    search_fields = ['title', 'description', 'short_description']
    ordering_fields = ['created_at', 'title', 'lesson_count']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseListSerializer
    
    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, slug=None):
        """
        Enroll the current user in a course.
        """
        course = self.get_object()
        user = request.user
        
        # Check if already enrolled
        if Enrollment.objects.filter(user=user, course=course).exists():
            return Response(
                {"detail": "You are already enrolled in this course."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create enrollment
        enrollment = Enrollment.objects.create(user=user, course=course)
        
        # Create lesson progress records for all published lessons
        lessons = course.lessons.filter(is_published=True)
        lesson_progress_objects = [
            LessonProgress(enrollment=enrollment, lesson=lesson)
            for lesson in lessons
        ]
        LessonProgress.objects.bulk_create(lesson_progress_objects)
        
        return Response(
            {"detail": "Successfully enrolled in the course."},
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_courses(self, request):
        """
        Get courses the current user is enrolled in.
        """
        user = request.user
        enrollments = Enrollment.objects.filter(user=user)
        
        # Filter by status if provided
        status_param = request.query_params.get('status')
        if status_param:
            enrollments = enrollments.filter(status=status_param)
        
        courses = Course.objects.filter(
            enrollments__in=enrollments
        ).annotate(lesson_count=Count('lessons'))
        
        page = self.paginate_queryset(courses)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(courses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def teaching(self, request):
        """
        Get courses the current user is teaching.
        """
        user = request.user
        courses = Course.objects.filter(
            instructor=user
        ).annotate(lesson_count=Count('lessons'))
        
        page = self.paginate_queryset(courses)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(courses, many=True)
        return Response(serializer.data)

class LessonViewSet(viewsets.ModelViewSet):
    """
    API endpoint for course lessons.
    """
    serializer_class = LessonSerializer
    permission_classes = [IsInstructorOrReadOnly]
    lookup_field = 'slug'
    
    def get_queryset(self):
        course_slug = self.kwargs.get('course_slug')
        if course_slug:
            return Lesson.objects.filter(course__slug=course_slug)
        return Lesson.objects.all()
    
    def perform_create(self, serializer):
        course_slug = self.kwargs.get('course_slug')
        course = Course.objects.get(slug=course_slug)
        
        # Check if user is the instructor
        if course.instructor != self.request.user:
            self.permission_denied(self.request, message="You are not the instructor of this course.")
        
        serializer.save(course=course)
    
    @action(detail=True, methods=['post'], permission_classes=[IsEnrolledOrInstructor])
    def mark_complete(self, request, course_slug=None, slug=None):
        """
        Mark a lesson as completed.
        """
        lesson = self.get_object()
        user = request.user
        
        try:
            enrollment = Enrollment.objects.get(user=user, course__slug=course_slug)
            lesson_progress, created = LessonProgress.objects.get_or_create(
                enrollment=enrollment,
                lesson=lesson,
                defaults={'status': 'not_started'}
            )
            
            # Update progress
            lesson_progress.status = 'completed'
            if not lesson_progress.started_at:
                lesson_progress.started_at = timezone.now()
            lesson_progress.completed_at = timezone.now()
            lesson_progress.save()
            
            # Update overall course progress
            total_lessons = enrollment.course.lessons.filter(is_published=True).count()
            completed_lessons = LessonProgress.objects.filter(
                enrollment=enrollment,
                status='completed'
            ).count()
            
            if total_lessons > 0:
                progress_percentage = (completed_lessons / total_lessons) * 100
                enrollment.progress = progress_percentage
                
                # Mark course as completed if all lessons are done
                if completed_lessons == total_lessons:
                    enrollment.status = 'completed'
                    enrollment.completed_at = timezone.now()
                
                enrollment.save()
            
            return Response({
                "detail": "Lesson marked as completed.",
                "progress": enrollment.progress
            })
            
        except Enrollment.DoesNotExist:
            return Response(
                {"detail": "You are not enrolled in this course."},
                status=status.HTTP_400_BAD_REQUEST
            )

class QuizViewSet(viewsets.ModelViewSet):
    """
    API endpoint for quizzes.
    """
    serializer_class = QuizSerializer
    permission_classes = [IsInstructorOrReadOnly]
    
    def get_queryset(self):
        lesson_id = self.kwargs.get('lesson_id')
        if lesson_id:
            return Quiz.objects.filter(lesson_id=lesson_id)
        return Quiz.objects.all()
    
    def perform_create(self, serializer):
        lesson_id = self.kwargs.get('lesson_id')
        lesson = Lesson.objects.get(id=lesson_id)
        
        # Check if user is the instructor
        if lesson.course.instructor != self.request.user:
            self.permission_denied(self.request, message="You are not the instructor of this course.")
        
        serializer.save(lesson=lesson)
    
    @action(detail=True, methods=['post'], permission_classes=[IsEnrolledOrInstructor])
    def submit(self, request, pk=None):
        """
        Submit answers for a quiz.
        """
        quiz = self.get_object()
        user = request.user
        
        # Validate submission data
        serializer = QuizSubmissionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Create quiz attempt
        quiz_attempt = QuizAttempt.objects.create(
            user=user,
            quiz=quiz,
            time_taken=serializer.validated_data['time_taken'],
            is_completed=True,
            completed_at=timezone.now()
        )
        
        # Process responses
        total_points = 0
        earned_points = 0
        
        for response_data in serializer.validated_data['responses']:
            question_id = response_data.get('question_id')
            question = Question.objects.get(id=question_id, quiz=quiz)
            total_points += question.points
            
            # Create response object
            quiz_response = QuizResponse.objects.create(
                attempt=quiz_attempt,
                question=question
            )
            
            # Handle different question types
            if question.question_type in ['multiple_choice', 'true_false']:
                selected_answer_ids = response_data.get('answer_ids', [])
                selected_answers = Answer.objects.filter(id__in=selected_answer_ids, question=question)
                quiz_response.selected_answers.set(selected_answers)
                
                # Check if correct (all correct answers selected and no incorrect ones)
                correct_answers = Answer.objects.filter(question=question, is_correct=True)
                if set(selected_answers.filter(is_correct=True)) == set(correct_answers) and not selected_answers.filter(is_correct=False).exists():
                    quiz_response.is_correct = True
                    quiz_response.score = question.points
                    earned_points += question.points
                
            elif question.question_type == 'short_answer':
                text_response = response_data.get('text_response', '')
                quiz_response.text_response = text_response
                
                # Simple exact match for short answer
                if text_response.lower().strip() == question.answer_explanation.lower().strip():
                    quiz_response.is_correct = True
                    quiz_response.score = question.points
                    earned_points += question.points
                
            elif question.question_type == 'essay':
                text_response = response_data.get('text_response', '')
                quiz_response.text_response = text_response
                
                # Queue essay for AI grading
                grade_essay_response.delay(quiz_response.id, question.answer_explanation)
            
            quiz_response.save()
        
        # Calculate and save score (excluding essays which will be graded asynchronously)
        if total_points > 0:
            quiz_attempt.score = (earned_points / total_points) * 100
        quiz_attempt.save()
        
        return Response({
            "detail": "Quiz submitted successfully.",
            "attempt_id": quiz_attempt.id,
            "score": quiz_attempt.score
        })

class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for course enrollments.
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """
        Get detailed progress for an enrollment.
        """
        enrollment = self.get_object()
        lesson_progress = LessonProgress.objects.filter(enrollment=enrollment)
        serializer = LessonProgressSerializer(lesson_progress, many=True)
        return Response(serializer.data)

class LessonProgressViewSet(viewsets.ModelViewSet):
    """
    API endpoint for lesson progress.
    """
    serializer_class = LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return LessonProgress.objects.filter(enrollment__user=self.request.user)
    
    def perform_update(self, serializer):
        instance = serializer.instance
        status_changed = 'status' in serializer.validated_data and serializer.validated_data['status'] != instance.status
        
        # Set timestamps based on status changes
        if status_changed:
            new_status = serializer.validated_data['status']
            if new_status == 'in_progress' and not instance.started_at:
                serializer.validated_data['started_at'] = timezone.now()
            elif new_status == 'completed' and not instance.completed_at:
                serializer.validated_data['completed_at'] = timezone.now()
        
        serializer.save()
        
        # Update overall course progress
        enrollment = instance.enrollment
        total_lessons = enrollment.course.lessons.filter(is_published=True).count()
        completed_lessons = LessonProgress.objects.filter(
            enrollment=enrollment,
            status='completed'
        ).count()
        
        if total_lessons > 0:
            progress_percentage = (completed_lessons / total_lessons) * 100
            enrollment.progress = progress_percentage
            
            # Mark course as completed if all lessons are done
            if completed_lessons == total_lessons:
                enrollment.status = 'completed'
                enrollment.completed_at = timezone.now()
            
            enrollment.save()

class QuizAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for quiz attempts.
    """
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user)

