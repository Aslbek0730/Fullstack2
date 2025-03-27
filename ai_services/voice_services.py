import os
import tempfile
import uuid
from pathlib import Path
import requests
from django.conf import settings
from openai import OpenAI
from pydub import AudioSegment
from gtts import gTTS

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def transcribe_audio(audio_file_path):
    """
    Transcribe audio to text using OpenAI's Whisper API.
    
    Args:
        audio_file_path: Path to the audio file
        
    Returns:
        str: Transcribed text
    """
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcription.text
    except Exception as e:
        print(f"Error transcribing audio: {str(e)}")
        return None

def text_to_speech(text, language='en', output_format='mp3'):
    """
    Convert text to speech using gTTS.
    
    Args:
        text: Text to convert to speech
        language: Language code (default: 'en')
        output_format: Output audio format (default: 'mp3')
        
    Returns:
        str: Path to the generated audio file
    """
    try:
        # Create a temporary file
        temp_dir = Path(settings.MEDIA_ROOT) / 'tts_audio'
        os.makedirs(temp_dir, exist_ok=True)
        
        file_name = f"{uuid.uuid4()}.{output_format}"
        file_path = temp_dir / file_name
        
        # Generate speech
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(str(file_path))
        
        return str(file_path)
    except Exception as e:
        print(f"Error converting text to speech: {str(e)}")
        return None

def convert_lesson_to_audio(lesson_id, language='en'):
    """
    Convert a lesson's content to audio.
    
    Args:
        lesson_id: ID of the lesson
        language: Language code (default: 'en')
        
    Returns:
        str: URL to the generated audio file
    """
    from courses.models import Lesson
    
    try:
        lesson = Lesson.objects.get(id=lesson_id)
        
        # Extract text content from lesson
        content = lesson.content
        
        # Convert HTML to plain text (simple approach)
        # For a more robust solution, consider using a library like BeautifulSoup
        import re
        plain_text = re.sub('<[^<]+?>', '', content)
        
        # Generate audio file
        audio_path = text_to_speech(plain_text, language)
        
        if audio_path:
            # Get relative path for URL
            relative_path = os.path.relpath(audio_path, settings.MEDIA_ROOT)
            url = f"{settings.MEDIA_URL}{relative_path}"
            return url
        
        return None
    except Exception as e:
        print(f"Error converting lesson to audio: {str(e)}")
        return None

def process_voice_command(audio_file_path, user):
    """
    Process a voice command from the user.
    
    Args:
        audio_file_path: Path to the audio file
        user: User object
        
    Returns:
        dict: Response with action and data
    """
    try:
        # Transcribe the audio
        transcription = transcribe_audio(audio_file_path)
        
        if not transcription:
            return {
                'success': False,
                'message': 'Failed to transcribe audio'
            }
        
        # Process the command
        command_response = process_command_text(transcription, user)
        
        # Generate audio response if needed
        if command_response.get('speak_response', False):
            response_text = command_response.get('message', '')
            audio_path = text_to_speech(response_text)
            
            if audio_path:
                # Get relative path for URL
                relative_path = os.path.relpath(audio_path, settings.MEDIA_ROOT)
                command_response['audio_url'] = f"{settings.MEDIA_URL}{relative_path}"
        
        return command_response
    
    except Exception as e:
        print(f"Error processing voice command: {str(e)}")
        return {
            'success': False,
            'message': 'Error processing voice command'
        }

def process_command_text(command_text, user):
    """
    Process a text command from the user.
    
    Args:
        command_text: Text command
        user: User object
        
    Returns:
        dict: Response with action and data
    """
    from courses.models import Course, Enrollment, Lesson
    
    # Convert to lowercase for easier matching
    command = command_text.lower()
    
    # Check for course-related commands
    if 'find course' in command or 'search course' in command or 'search for course' in command:
        # Extract search term
        search_terms = command.split('course')[-1].strip()
        if search_terms:
            courses = Course.objects.filter(title__icontains=search_terms, is_published=True)[:5]
            
            if courses:
                course_list = [{'id': c.id, 'title': c.title, 'slug': c.slug} for c in courses]
                return {
                    'success': True,
                    'action': 'search_courses',
                    'data': course_list,
                    'message': f"I found {len(course_list)} courses matching '{search_terms}'",
                    'speak_response': True
                }
            else:
                return {
                    'success': True,
                    'action': 'search_courses',
                    'data': [],
                    'message': f"I couldn't find any courses matching '{search_terms}'",
                    'speak_response': True
                }
    
    # Check for enrollment-related commands
    elif 'my courses' in command or 'enrolled courses' in command:
        enrollments = Enrollment.objects.filter(user=user)
        if enrollments:
            courses = [{'id': e.course.id, 'title': e.course.title, 'slug': e.course.slug, 
                        'progress': e.progress} for e in enrollments]
            return {
                'success': True,
                'action': 'list_enrollments',
                'data': courses,
                'message': f"You are enrolled in {len(courses)} courses",
                'speak_response': True
            }
        else:
            return {
                'success': True,
                'action': 'list_enrollments',
                'data': [],
                'message': "You are not enrolled in any courses yet",
                'speak_response': True
            }
    
    # Check for lesson-related commands
    elif 'continue learning' in command or 'resume course' in command:
        # Find the most recently accessed lesson
        from courses.models import LessonProgress
        
        recent_progress = LessonProgress.objects.filter(
            enrollment__user=user
        ).order_by('-last_accessed_at').first()
        
        if recent_progress:
            lesson = recent_progress.lesson
            course = lesson.course
            
            return {
                'success': True,
                'action': 'continue_learning',
                'data': {
                    'course_id': course.id,
                    'course_slug': course.slug,
                    'lesson_id': lesson.id,
                    'lesson_slug': lesson.slug,
                    'lesson_title': lesson.title
                },
                'message': f"Resuming {lesson.title} in {course.title}",
                'speak_response': True
            }
        else:
            return {
                'success': True,
                'action': 'continue_learning',
                'data': None,
                'message': "You don't have any lessons in progress",
                'speak_response': True
            }
    
    # If no specific command is recognized, treat as a question for the AI assistant
    else:
        from .services import get_ai_response
        
        # Create a temporary chat session for this command
        from .models import ChatSession, ChatMessage
        
        session, created = ChatSession.objects.get_or_create(
            user=user,
            title="Voice Assistant Session",
            defaults={'title': "Voice Assistant Session"}
        )
        
        # Save the user's message
        user_message = ChatMessage.objects.create(
            session=session,
            role='user',
            content=command_text
        )
        
        # Get context from previous messages
        context_messages = ChatMessage.objects.filter(session=session).order_by('created_at')
        
        # Get AI response
        ai_response = get_ai_response(command_text, context_messages, user)
        
        # Save AI response
        assistant_message = ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=ai_response
        )
        
        return {
            'success': True,
            'action': 'ai_response',
            'data': {
                'question': command_text,
                'answer': ai_response
            },
            'message': ai_response,
            'speak_response': True
        }

