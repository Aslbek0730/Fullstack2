import os
import pickle
import numpy as np
from django.conf import settings
from openai import OpenAI
from django.db.models import Count, Avg, Q
from courses.models import Course, Enrollment, LessonProgress, QuizAttempt
from users.models import LearningActivity
from .models import UserEmbedding, CourseEmbedding, AIFeedback

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_ai_response(message, context_messages, user):
    """
    Get a response from the AI assistant.
    
    Args:
        message: The user's message
        context_messages: Previous messages in the conversation
        user: The user object
        
    Returns:
        str: The AI assistant's response
    """
    # Format context messages for OpenAI
    formatted_messages = []
    
    # Add system message with context about the user
    system_message = f"""
    You are an AI learning assistant for the EduLearn platform. 
    Your goal is to help users learn and understand course materials.
    
    User information:
    - Name: {user.first_name} {user.last_name}
    - Learning interests: {', '.join(user.interests) if user.interests else 'Not specified'}
    - Learning style: {user.learning_style if user.learning_style else 'Not specified'}
    
    Respond in a helpful, educational manner. If asked about course content you're not familiar with,
    suggest the user check the course materials or contact their instructor.
    """
    formatted_messages.append({"role": "system", "content": system_message})
    
    # Add conversation history (up to last 10 messages)
    for msg in context_messages.order_by('-created_at')[:10][::-1]:
        formatted_messages.append({"role": msg.role, "content": msg.content})
    
    # Add the current message
    formatted_messages.append({"role": "user", "content": message})
    
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=formatted_messages,
            max_tokens=1000,
            temperature=0.7,
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        # Log the error and return a fallback message
        print(f"Error getting AI response: {str(e)}")
        return "I'm sorry, I'm having trouble processing your request right now. Please try again later."

def generate_embeddings(text):
    """
    Generate embeddings for text using OpenAI's embedding model.
    
    Args:
        text: The text to generate embeddings for
        
    Returns:
        numpy.ndarray: The embedding vector
    """
    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return np.array(response.data[0].embedding)
    
    except Exception as e:
        print(f"Error generating embeddings: {str(e)}")
        return np.zeros(1536)  # Default embedding dimension for text-embedding-ada-002

def update_user_embedding(user):
    """
    Update the embedding vector for a user based on their activities.
    
    Args:
        user: The user object
    """
    # Collect user data for embedding
    interests = ', '.join(user.interests) if user.interests else ''
    learning_style = user.learning_style if user.learning_style else ''
    
    # Get recent learning activities
    activities = LearningActivity.objects.filter(user=user).order_by('-created_at')[:50]
    activity_text = ' '.join([f"{a.activity_type} {a.content_type}" for a in activities])
    
    # Get enrolled courses
    enrollments = Enrollment.objects.filter(user=user)
    enrolled_courses = Course.objects.filter(enrollments__in=enrollments)
    course_text = ' '.join([f"{c.title} {c.description}" for c in enrolled_courses])
    
    # Combine all text
    user_text = f"Interests: {interests}. Learning style: {learning_style}. Activities: {activity_text}. Courses: {course_text}"
    
    # Generate embedding
    embedding_vector = generate_embeddings(user_text)
    
    # Save or update embedding
    user_embedding, created = UserEmbedding.objects.get_or_create(user=user)
    user_embedding.embedding_vector = pickle.dumps(embedding_vector)
    user_embedding.save()

def update_course_embedding(course):
    """
    Update the embedding vector for a course.
    
    Args:
        course: The course object
    """
    # Collect course data for embedding
    course_text = f"{course.title}. {course.description}. {course.short_description}. Level: {course.level}."
    
    # Add lesson information
    lessons = course.lessons.all()
    lesson_text = ' '.join([f"{l.title}. {l.description}" for l in lessons])
    
    # Combine all text
    full_text = f"{course_text} {lesson_text}"
    
    # Generate embedding
    embedding_vector = generate_embeddings(full_text)
    
    # Save or update embedding
    course_embedding, created = CourseEmbedding.objects.get_or_create(course=course)
    course_embedding.embedding_vector = pickle.dumps(embedding_vector)
    course_embedding.save()

def generate_course_recommendations(user, count=5, include_enrolled=False):
    """
    Generate personalized course recommendations for a user.
    
    Args:
        user: The user object
        count: Number of recommendations to return
        include_enrolled: Whether to include courses the user is already enrolled in
        
    Returns:
        list: List of recommended course objects with similarity scores
    """
    try:
        # Get user embedding
        try:
            user_embedding = UserEmbedding.objects.get(user=user)
            user_vector = pickle.loads(user_embedding.embedding_vector)
        except UserEmbedding.DoesNotExist:
            # Create embedding if it doesn't exist
            update_user_embedding(user)
            user_embedding = UserEmbedding.objects.get(user=user)
            user_vector = pickle.loads(user_embedding.embedding_vector)
        
        # Get all course embeddings
        course_embeddings = CourseEmbedding.objects.all()
        
        # Calculate similarity scores
        similarities = []
        for ce in course_embeddings:
            course_vector = pickle.loads(ce.embedding_vector)
            
            # Calculate cosine similarity
            similarity = np.dot(user_vector, course_vector) / (np.linalg.norm(user_vector) * np.linalg.norm(course_vector))
            
            similarities.append({
                'course': ce.course,
                'similarity': float(similarity)
            })
        
        # Filter out enrolled courses if needed
        if not include_enrolled:
            enrolled_course_ids = Enrollment.objects.filter(user=user).values_list('course_id', flat=True)
            similarities = [s for s in similarities if s['course'].id not in enrolled_course_ids]
        
        # Sort by similarity and return top N
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        top_recommendations = similarities[:count]
        
        # Format response
        result = []
        for rec in top_recommendations:
            course = rec['course']
            result.append({
                'id': course.id,
                'title': course.title,
                'slug': course.slug,
                'short_description': course.short_description,
                'level': course.level,
                'similarity_score': rec['similarity'],
                'thumbnail': course.thumbnail.url if course.thumbnail else None,
            })
        
        return result
    
    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")
        
        # Fallback to popularity-based recommendations
        popular_courses = Course.objects.annotate(
            enrollment_count=Count('enrollments')
        ).order_by('-enrollment_count')[:count]
        
        if not include_enrolled:
            enrolled_course_ids = Enrollment.objects.filter(user=user).values_list('course_id', flat=True)
            popular_courses = popular_courses.exclude(id__in=enrolled_course_ids)
        
        result = []
        for course in popular_courses:
            result.append({
                'id': course.id,
                'title': course.title,
                'slug': course.slug,
                'short_description': course.short_description,
                'level': course.level,
                'similarity_score': 0.0,  # No similarity score for fallback
                'thumbnail': course.thumbnail.url if course.thumbnail else None,
            })
        
        return result

def grade_essay(essay_text, rubric='', max_score=100):
    """
    Grade an essay using AI.
    
    Args:
        essay_text: The essay text to grade
        rubric: Grading rubric or criteria
        max_score: Maximum possible score
        
    Returns:
        tuple: (score, feedback)
    """
    try:
        # Prepare prompt for the AI
        if rubric:
            prompt = f"""
            Please grade the following essay according to this rubric:
            
            {rubric}
            
            The maximum score is {max_score}.
            
            Essay:
            {essay_text}
            
            Provide a detailed assessment with specific feedback on strengths and areas for improvement.
            Format your response as:
            
            Score: [numerical score out of {max_score}]
            
            Feedback:
            [detailed feedback]
            """
        else:
            prompt = f"""
            Please grade the following essay on a scale of 0 to {max_score}.
            Consider factors such as:
            - Clarity and coherence
            - Quality of arguments and evidence
            - Grammar and writing style
            - Organization and structure
            
            Essay:
            {essay_text}
            
            Provide a detailed assessment with specific feedback on strengths and areas for improvement.
            Format your response as:
            
            Score: [numerical score out of {max_score}]
            
            Feedback:
            [detailed feedback]
            """
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert educator who grades essays fairly and provides constructive feedback."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3,
        )
        
        response_text = response.choices[0].message.content
        
        # Extract score and feedback
        try:
            # Try to parse the score from the response
            score_line = [line for line in response_text.split('\n') if line.lower().startswith('score:')]
            if score_line:
                score_text = score_line[0].split(':', 1)[1].strip()
                # Extract the first number from the score text
                import re
                score_match = re.search(r'\d+(\.\d+)?', score_text)
                if score_match:
                    score = float(score_match.group(0))
                else:
                    score = max_score / 2  # Default to middle score if parsing fails
            else:
                score = max_score / 2
            
            # Extract feedback (everything after "Feedback:")
            feedback_parts = response_text.split('Feedback:', 1)
            if len(feedback_parts) > 1:
                feedback = feedback_parts[1].strip()
            else:
                feedback = response_text  # Use full response if can't parse
            
            return score, feedback
            
        except Exception as parsing_error:
            print(f"Error parsing AI response: {str(parsing_error)}")
            return max_score / 2, response_text  # Return middle score and full response
    
    except Exception as e:
        print(f"Error grading essay: {str(e)}")
        return 0, "Error processing essay. Please try again later."

def grade_essay_response(response_id, answer_key=''):
    """
    Grade a quiz essay response using AI.
    
    Args:
        response_id: The ID of the QuizResponse object
        answer_key: The answer key or rubric for grading
    """
    from courses.models import QuizResponse
    
    try:
        # Get the response object
        response = QuizResponse.objects.get(id=response_id)
        
        # Get the essay text
        essay_text = response.text_response
        
        # Get the question
        question = response.question
        
        # Get the maximum points
        max_points = question.points
        
        # Grade the essay
        score, feedback = grade_essay(
            essay_text,
            rubric=answer_key or question.answer_explanation,
            max_score=max_points
        )
        
        # Update the response
        response.score = score
        response.feedback = feedback
        response.is_correct = score >= (max_points * 0.7)  # Consider correct if score is at least 70%
        response.save()
        
        # Update the overall quiz attempt score
        attempt = response.attempt
        total_points = attempt.quiz.questions.aggregate(total=models.Sum('points'))['total'] or 1
        earned_points = QuizResponse.objects.filter(attempt=attempt).aggregate(earned=models.Sum('score'))['earned'] or 0
        
        attempt.score = (earned_points / total_points) * 100
        attempt.save()
        
        # Create AI feedback record
        AIFeedback.objects.create(
            user=attempt.user,
            content_type='quiz_response',
            content_id=response.id,
            feedback=feedback,
            score=score
        )
        
    except Exception as e:
        print(f"Error grading essay response {response_id}: {str(e)}")

