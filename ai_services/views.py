from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import ChatSession, ChatMessage, AIFeedback
from .serializers import (
    ChatSessionSerializer, ChatMessageSerializer, ChatMessageCreateSerializer,
    AIFeedbackSerializer, CourseRecommendationRequestSerializer,
    EssayGradingRequestSerializer
)
from .services import (
    get_ai_response, generate_course_recommendations,
    grade_essay, update_user_embedding
)
from .voice_services import (
    transcribe_audio, text_to_speech, convert_lesson_to_audio,
    process_voice_command
)
from .assessment_services import (
    analyze_quiz_results, generate_personalized_feedback,
    identify_knowledge_gaps, generate_study_plan
)

class ChatSessionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for chat sessions.
    """
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """
        Send a message to the AI assistant and get a response.
        """
        session = self.get_object()
        serializer = ChatMessageCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Save user message
            user_message = ChatMessage.objects.create(
                session=session,
                role='user',
                content=serializer.validated_data['content']
            )
            
            # Get context from previous messages
            context_messages = ChatMessage.objects.filter(session=session).order_by('created_at')
            
            # Get AI response
            ai_response = get_ai_response(
                user_message.content,
                context_messages,
                request.user
            )
            
            # Save AI response
            assistant_message = ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=ai_response
            )
            
            # Update session timestamp
            session.save()  # This will update the updated_at field
            
            # Return both messages
            return Response({
                'user_message': ChatMessageSerializer(user_message).data,
                'assistant_message': ChatMessageSerializer(assistant_message).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AIFeedbackViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for AI feedback.
    """
    serializer_class = AIFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AIFeedback.objects.filter(user=self.request.user)

class RecommendationViewSet(viewsets.ViewSet):
    """
    API endpoint for AI-powered recommendations.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def courses(self, request):
        """
        Get personalized course recommendations.
        """
        serializer = CourseRecommendationRequestSerializer(data=request.data)
        if serializer.is_valid():
            count = serializer.validated_data['count']
            include_enrolled = serializer.validated_data['include_enrolled']
            
            # Update user embedding before generating recommendations
            update_user_embedding(request.user)
            
            # Get recommendations
            recommendations = generate_course_recommendations(
                request.user,
                count=count,
                include_enrolled=include_enrolled
            )
            
            return Response(recommendations)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def grade_essay(self, request):
        """
        Grade an essay using AI.
        """
        serializer = EssayGradingRequestSerializer(data=request.data)
        if serializer.is_valid():
            essay_text = serializer.validated_data['essay_text']
            rubric = serializer.validated_data.get('rubric', '')
            max_score = serializer.validated_data['max_score']
            
            # Grade the essay
            score, feedback = grade_essay(essay_text, rubric, max_score)
            
            # Save feedback
            AIFeedback.objects.create(
                user=request.user,
                content_type='essay',
                content_id=0,  # No specific content ID for direct grading
                feedback=feedback,
                score=score
            )
            
            return Response({
                'score': score,
                'feedback': feedback
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VoiceAssistantViewSet(viewsets.ViewSet):
    """
    API endpoint for voice assistant features.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def transcribe(self, request):
        """
        Transcribe audio to text.
        """
        if 'audio' not in request.FILES:
            return Response(
                {"error": "No audio file provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        audio_file = request.FILES['audio']
        
        # Save the file temporarily
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            for chunk in audio_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        try:
            # Transcribe the audio
            transcription = transcribe_audio(temp_file_path)
            
            # Clean up the temporary file
            os.unlink(temp_file_path)
            
            if transcription:
                return Response({
                    'transcription': transcription
                })
            else:
                return Response(
                    {"error": "Failed to transcribe audio"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        except Exception as e:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def text_to_speech(self, request):
        """
        Convert text to speech.
        """
        if 'text' not in request.data:
            return Response(
                {"error": "No text provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        text = request.data['text']
        language = request.data.get('language', 'en')
        
        try:
            # Convert text to speech
            audio_path = text_to_speech(text, language)
            
            if audio_path:
                # Get relative path for URL
                from django.conf import settings
                import os
                
                relative_path = os.path.relpath(audio_path, settings.MEDIA_ROOT)
                url = f"{settings.MEDIA_URL}{relative_path}"
                
                return Response({
                    'audio_url': url
                })
            else:
                return Response(
                    {"error": "Failed to convert text to speech"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def lesson_audio(self, request):
        """
        Convert a lesson's content to audio.
        """
        if 'lesson_id' not in request.data:
            return Response(
                {"error": "No lesson_id provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lesson_id = request.data['lesson_id']
        language = request.data.get('language', 'en')
        
        try:
            # Convert lesson to audio
            audio_url = convert_lesson_to_audio(lesson_id, language)
            
            if audio_url:
                return Response({
                    'audio_url': audio_url
                })
            else:
                return Response(
                    {"error": "Failed to convert lesson to audio"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def command(self, request):
        """
        Process a voice command.
        """
        if 'audio' not in request.FILES and 'text' not in request.data:
            return Response(
                {"error": "No audio file or text provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if 'audio' in request.FILES:
                audio_file = request.FILES['audio']
                
                # Save the file temporarily
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                    for chunk in audio_file.chunks():
                        temp_file.write(chunk)
                    temp_file_path = temp_file.name
                
                # Process the command
                response = process_voice_command(temp_file_path, request.user)
                
                # Clean up the temporary file
                os.unlink(temp_file_path)
                
                return Response(response)
            
            else:  # Text command
                text = request.data['text']
                
                # Import the function to process text commands
                from .voice_services import process_command_text
                
                # Process the command
                response = process_command_text(text, request.user)
                
                return Response(response)
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AssessmentViewSet(viewsets.ViewSet):
    """
    API endpoint for assessment and feedback features.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def quiz_analysis(self, request):
        """
        Get analysis of quiz results.
        """
        quiz_id = request.query_params.get('quiz_id')
        user_id = request.query_params.get('user_id')
        
        if not quiz_id:
            return Response(
                {"error": "quiz_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If user_id is not provided, use the current user
        if not user_id:
            user_id = request.user.id
        
        # Check permissions if analyzing another user's results
        if int(user_id) != request.user.id:
            # Only instructors can view other users' results
            from courses.models import Course, Quiz
            
            try:
                quiz = Quiz.objects.get(id=quiz_id)
                course = quiz.lesson.course
                
                if course.instructor != request.user:
                    return Response(
                        {"error": "You don't have permission to view this user's results"},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            except Exception:
                return Response(
                    {"error": "Quiz not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Get quiz analysis
        analysis = analyze_quiz_results(quiz_id, user_id)
        
        if analysis:
            return Response(analysis)
        else:
            return Response(
                {"error": "Failed to analyze quiz results"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def personalized_feedback(self, request):
        """
        Get personalized feedback based on performance.
        """
        course_id = request.query_params.get('course_id')
        
        # Generate feedback for the current user
        feedback = generate_personalized_feedback(request.user.id, course_id)
        
        return Response(feedback)
    
    @action(detail=False, methods=['get'])
    def knowledge_gaps(self, request):
        """
        Identify knowledge gaps based on quiz performance.
        """
        # Identify gaps for the current user
        gaps = identify_knowledge_gaps(request.user.id)
        
        return Response(gaps)
    
    @action(detail=False, methods=['post'])
    def study_plan(self, request):
        """
        Generate a personalized study plan.
        """
        course_id = request.data.get('course_id')
        target_date = request.data.get('target_date')
        
        # Generate study plan for the current user
        plan = generate_study_plan(request.user.id, course_id, target_date)
        
        return Response(plan)

