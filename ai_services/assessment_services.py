import numpy as np
from django.db.models import Avg, Count, Sum, F, Q
from django.utils import timezone
from openai import OpenAI
from django.conf import settings

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def analyze_quiz_results(quiz_id, user_id=None):
    """
    Analyze quiz results for a specific quiz and optionally a specific user.
    
    Args:
        quiz_id: ID of the quiz
        user_id: Optional user ID to filter results
        
    Returns:
        dict: Analysis results
    """
    from courses.models import Quiz, QuizAttempt, QuizResponse
    
    try:
        quiz = Quiz.objects.get(id=quiz_id)
        
        # Base query for attempts
        attempts_query = QuizAttempt.objects.filter(quiz=quiz, is_completed=True)
        
        # Filter by user if specified
        if user_id:
            attempts_query = attempts_query.filter(user_id=user_id)
        
        # Get aggregate statistics
        stats = attempts_query.aggregate(
            avg_score=Avg('score'),
            avg_time=Avg('time_taken'),
            attempt_count=Count('id'),
            max_score=Max('score'),
            min_score=Min('score')
        )
        
        # Get question-level statistics
        question_stats = []
        for question in quiz.questions.all():
            q_stats = QuizResponse.objects.filter(
                question=question,
                attempt__in=attempts_query
            ).aggregate(
                correct_count=Count('id', filter=Q(is_correct=True)),
                total_count=Count('id'),
                avg_score=Avg('score')
            )
            
            # Calculate percentage correct
            correct_pct = 0
            if q_stats['total_count'] > 0:
                correct_pct = (q_stats['correct_count'] / q_stats['total_count']) * 100
            
            question_stats.append({
                'question_id': question.id,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'correct_percentage': correct_pct,
                'avg_score': q_stats['avg_score'] or 0,
                'attempt_count': q_stats['total_count']
            })
        
        # Get user's most recent attempt if user_id is provided
        user_attempt = None
        if user_id and attempts_query.exists():
            latest_attempt = attempts_query.order_by('-completed_at').first()
            
            user_attempt = {
                'attempt_id': latest_attempt.id,
                'score': latest_attempt.score,
                'time_taken': latest_attempt.time_taken,
                'completed_at': latest_attempt.completed_at,
                'responses': []
            }
            
            # Get detailed responses
            for response in latest_attempt.responses.all():
                user_attempt['responses'].append({
                    'question_id': response.question.id,
                    'question_text': response.question.question_text,
                    'is_correct': response.is_correct,
                    'score': response.score,
                    'feedback': response.feedback
                })
        
        return {
            'quiz_id': quiz.id,
            'quiz_title': quiz.title,
            'statistics': stats,
            'question_statistics': question_stats,
            'user_attempt': user_attempt
        }
    
    except Exception as e:
        print(f"Error analyzing quiz results: {str(e)}")
        return None

def generate_personalized_feedback(user_id, course_id=None):
    """
    Generate personalized feedback for a user based on their performance.
    
    Args:
        user_id: User ID
        course_id: Optional course ID to filter results
        
    Returns:
        dict: Personalized feedback
    """
    from courses.models import Enrollment, LessonProgress, QuizAttempt
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
        
        # Get enrollments
        enrollments_query = Enrollment.objects.filter(user=user)
        if course_id:
            enrollments_query = enrollments_query.filter(course_id=course_id)
        
        # If no enrollments, return early
        if not enrollments_query.exists():
            return {
                'user_id': user_id,
                'message': "No course data available for analysis",
                'recommendations': []
            }
        
        # Collect data for analysis
        course_data = []
        
        for enrollment in enrollments_query:
            course = enrollment.course
            
            # Get lesson progress
            lesson_progress = LessonProgress.objects.filter(enrollment=enrollment)
            completed_lessons = lesson_progress.filter(status='completed').count()
            total_lessons = lesson_progress.count()
            
            # Get quiz attempts
            quiz_attempts = QuizAttempt.objects.filter(
                user=user,
                quiz__lesson__course=course,
                is_completed=True
            )
            
            avg_score = quiz_attempts.aggregate(avg=Avg('score'))['avg'] or 0
            
            # Identify strengths and weaknesses based on quiz performance
            strengths = []
            weaknesses = []
            
            if quiz_attempts.exists():
                # Group quiz responses by question type and calculate average scores
                from courses.models import QuizResponse, Question
                from django.db.models import Avg, F, Q
                
                question_type_scores = QuizResponse.objects.filter(
                    attempt__in=quiz_attempts
                ).values(
                    'question__question_type'
                ).annotate(
                    avg_score=Avg('score'),
                    max_possible=Avg('question__points')
                )
                
                for item in question_type_scores:
                    question_type = item['question__question_type']
                    score_pct = (item['avg_score'] / item['max_possible']) * 100 if item['max_possible'] else 0
                    
                    if score_pct >= 80:
                        strengths.append(question_type)
                    elif score_pct <= 60:
                        weaknesses.append(question_type)
            
            course_data.append({
                'course_id': course.id,
                'course_title': course.title,
                'progress': enrollment.progress,
                'completed_lessons': completed_lessons,
                'total_lessons': total_lessons,
                'avg_quiz_score': avg_score,
                'strengths': strengths,
                'weaknesses': weaknesses
            })
        
        # Generate personalized feedback using AI
        feedback = generate_ai_feedback(user, course_data)
        
        return {
            'user_id': user_id,
            'course_data': course_data,
            'feedback': feedback
        }
    
    except Exception as e:
        print(f"Error generating personalized feedback: {str(e)}")
        return {
            'user_id': user_id,
            'message': "Error generating feedback",
            'error': str(e)
        }

def generate_ai_feedback(user, course_data):
    """
    Generate AI-powered feedback based on user performance data.
    
    Args:
        user: User object
        course_data: List of course performance data
        
    Returns:
        dict: AI-generated feedback
    """
    try:
        # Prepare prompt for the AI
        prompt = f"""
        I need to generate personalized learning feedback for a student based on their performance data.
        
        Student information:
        - Name: {user.first_name} {user.last_name}
        - Learning interests: {', '.join(user.interests) if user.interests else 'Not specified'}
        - Learning style: {user.learning_style if user.learning_style else 'Not specified'}
        
        Course performance data:
        """
        
        for course in course_data:
            prompt += f"""
            Course: {course['course_title']}
            - Progress: {course['progress']:.1f}%
            - Completed lessons: {course['completed_lessons']} of {course['total_lessons']}
            - Average quiz score: {course['avg_quiz_score']:.1f}%
            - Strengths: {', '.join(course['strengths']) if course['strengths'] else 'None identified'}
            - Weaknesses: {', '.join(course['weaknesses']) if course['weaknesses'] else 'None identified'}
            """
        
        prompt += """
        Please provide:
        1. A personalized assessment of the student's performance
        2. 3-5 specific recommendations for improvement
        3. Suggested learning resources or activities based on their performance
        
        Format your response as JSON with the following structure:
        {
            "assessment": "Overall assessment of performance",
            "recommendations": [
                "Specific recommendation 1",
                "Specific recommendation 2",
                ...
            ],
            "resources": [
                {
                    "title": "Resource title",
                    "description": "Brief description",
                    "type": "article|video|exercise|quiz"
                },
                ...
            ]
        }
        """
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert educational advisor who provides personalized learning feedback."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=1000,
            temperature=0.5,
        )
        
        response_text = response.choices[0].message.content
        
        # Parse JSON response
        import json
        feedback = json.loads(response_text)
        
        return feedback
    
    except Exception as e:
        print(f"Error generating AI feedback: {str(e)}")
        return {
            "assessment": "Unable to generate personalized assessment at this time.",
            "recommendations": [
                "Continue working through your course materials",
                "Review any lessons where you scored below 70%",
                "Reach out to instructors if you need additional help"
            ],
            "resources": []
        }

def identify_knowledge_gaps(user_id):
    """
    Identify knowledge gaps based on quiz performance.
    
    Args:
        user_id: User ID
        
    Returns:
        list: Identified knowledge gaps
    """
    from courses.models import QuizResponse, QuizAttempt
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
        
        # Get all completed quiz attempts
        attempts = QuizAttempt.objects.filter(
            user=user,
            is_completed=True
        )
        
        # If no attempts, return early
        if not attempts.exists():
            return []
        
        # Get incorrect responses
        incorrect_responses = QuizResponse.objects.filter(
            attempt__in=attempts,
            is_correct=False
        ).select_related('question', 'question__quiz', 'question__quiz__lesson')
        
        # Group by lesson to identify problem areas
        from collections import defaultdict
        
        lesson_issues = defaultdict(list)
        
        for response in incorrect_responses:
            lesson = response.question.quiz.lesson
            
            lesson_issues[lesson.id].append({
                'question_id': response.question.id,
                'question_text': response.question.question_text,
                'question_type': response.question.question_type,
                'score': response.score,
                'max_score': response.question.points
            })
        
        # Identify significant knowledge gaps (lessons with multiple incorrect answers)
        knowledge_gaps = []
        
        for lesson_id, issues in lesson_issues.items():
            if len(issues) >= 2:  # At least 2 incorrect answers in the lesson
                from courses.models import Lesson
                lesson = Lesson.objects.get(id=lesson_id)
                
                knowledge_gaps.append({
                    'lesson_id': lesson.id,
                    'lesson_title': lesson.title,
                    'course_id': lesson.course.id,
                    'course_title': lesson.course.title,
                    'issue_count': len(issues),
                    'issues': issues
                })
        
        # Sort by issue count (most problematic first)
        knowledge_gaps.sort(key=lambda x: x['issue_count'], reverse=True)
        
        return knowledge_gaps
    
    except Exception as e:
        print(f"Error identifying knowledge gaps: {str(e)}")
        return []

def generate_study_plan(user_id, course_id=None, target_date=None):
    """
    Generate a personalized study plan based on user performance and goals.
    
    Args:
        user_id: User ID
        course_id: Optional course ID to focus on
        target_date: Optional target completion date
        
    Returns:
        dict: Personalized study plan
    """
    from courses.models import Enrollment, LessonProgress, Course
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
        
        # Get enrollments
        enrollments_query = Enrollment.objects.filter(user=user, status='active')
        if course_id:
            enrollments_query = enrollments_query.filter(course_id=course_id)
        
        # If no enrollments, return early
        if not enrollments_query.exists():
            return {
                'user_id': user_id,
                'message': "No active courses found for study plan",
                'plan': []
            }
        
        # Calculate days until target date
        days_remaining = None
        if target_date:
            from datetime import datetime
            today = timezone.now().date()
            target = datetime.strptime(target_date, '%Y-%m-%d').date()
            days_remaining = (target - today).days
            
            if days_remaining <= 0:
                return {
                    'user_id': user_id,
                    'message': "Target date must be in the future",
                    'plan': []
                }
        
        # Collect course data
        courses_data = []
        
        for enrollment in enrollments_query:
            course = enrollment.course
            
            # Get incomplete lessons
            incomplete_lessons = LessonProgress.objects.filter(
                enrollment=enrollment
            ).exclude(
                status='completed'
            ).select_related('lesson')
            
            # Skip if all lessons are completed
            if not incomplete_lessons.exists():
                continue
            
            # Get knowledge gaps
            knowledge_gaps = identify_knowledge_gaps(user_id)
            problem_lesson_ids = [gap['lesson_id'] for gap in knowledge_gaps]
            
            # Prioritize lessons
            prioritized_lessons = []
            
            # First priority: Lessons with knowledge gaps
            for progress in incomplete_lessons:
                if progress.lesson.id in problem_lesson_ids:
                    prioritized_lessons.append({
                        'lesson_id': progress.lesson.id,
                        'lesson_title': progress.lesson.title,
                        'priority': 'high',
                        'status': progress.status,
                        'duration': progress.lesson.duration,
                        'order': progress.lesson.order
                    })
            
            # Second priority: Lessons in progress
            for progress in incomplete_lessons:
                if progress.status == 'in_progress' and progress.lesson.id not in problem_lesson_ids:
                    prioritized_lessons.append({
                        'lesson_id': progress.lesson.id,
                        'lesson_title': progress.lesson.title,
                        'priority': 'medium',
                        'status': progress.status,
                        'duration': progress.lesson.duration,
                        'order': progress.lesson.order
                    })
            
            # Third priority: Not started lessons
            for progress in incomplete_lessons:
                if progress.status == 'not_started' and progress.lesson.id not in problem_lesson_ids:
                    prioritized_lessons.append({
                        'lesson_id': progress.lesson.id,
                        'lesson_title': progress.lesson.title,
                        'priority': 'normal',
                        'status': progress.status,
                        'duration': progress.lesson.duration,
                        'order': progress.lesson.order
                    })
            
            # Sort by priority and then by lesson order
            prioritized_lessons.sort(key=lambda x: (
                0 if x['priority'] == 'high' else 1 if x['priority'] == 'medium' else 2,
                x['order']
            ))
            
            courses_data.append({
                'course_id': course.id,
                'course_title': course.title,
                'progress': enrollment.progress,
                'remaining_lessons': len(prioritized_lessons),
                'lessons': prioritized_lessons
            })
        
        # Generate study plan
        study_plan = generate_ai_study_plan(user, courses_data, days_remaining)
        
        return {
            'user_id': user_id,
            'target_date': target_date,
            'days_remaining': days_remaining,
            'courses': courses_data,
            'study_plan': study_plan
        }
    
    except Exception as e:
        print(f"Error generating study plan: {str(e)}")
        return {
            'user_id': user_id,
            'message': "Error generating study plan",
            'error': str(e),
            'plan': []
        }

def generate_ai_study_plan(user, courses_data, days_remaining=None):
    """
    Generate AI-powered study plan based on course data.
    
    Args:
        user: User object
        courses_data: List of course data
        days_remaining: Optional days until target date
        
    Returns:
        dict: AI-generated study plan
    """
    try:
        # Prepare prompt for the AI
        prompt = f"""
        I need to generate a personalized study plan for a student based on their course data.
        
        Student information:
        - Name: {user.first_name} {user.last_name}
        - Learning interests: {', '.join(user.interests) if user.interests else 'Not specified'}
        - Learning style: {user.learning_style if user.learning_style else 'Not specified'}
        """
        
        if days_remaining:
            prompt += f"\nThe student has {days_remaining} days to complete their courses.\n"
        
        prompt += "\nCourse data:\n"
        
        for course in courses_data:
            prompt += f"""
            Course: {course['course_title']}
            - Current progress: {course['progress']:.1f}%
            - Remaining lessons: {course['remaining_lessons']}
            
            Lessons to complete:
            """
            
            for lesson in course['lessons'][:10]:  # Limit to first 10 lessons to avoid token limits
                prompt += f"- {lesson['lesson_title']} (Priority: {lesson['priority']}, Duration: {lesson['duration']} minutes)\n"
        
        prompt += """
        Please create a structured study plan that:
        1. Distributes the workload evenly over the available time
        2. Prioritizes high-priority lessons
        3. Groups related topics together when possible
        4. Includes time for review and practice
        5. Accounts for the student's learning style
        
        Format your response as JSON with the following structure:
        {
            "overview": "Brief overview of the study plan",
            "recommendations": [
                "General recommendation 1",
                "General recommendation 2",
                ...
            ],
            "weekly_plan": [
                {
                    "week": 1,
                    "focus": "Main focus for this week",
                    "days": [
                        {
                            "day": "Monday",
                            "activities": [
                                {
                                    "course": "Course title",
                                    "lesson": "Lesson title",
                                    "duration": 30,
                                    "type": "lesson|review|practice"
                                },
                                ...
                            ]
                        },
                        ...
                    ]
                },
                ...
            ]
        }
        """
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert educational advisor who creates personalized study plans."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=2000,
            temperature=0.5,
        )
        
        response_text = response.choices[0].message.content
        
        # Parse JSON response
        import json
        study_plan = json.loads(response_text)
        
        return study_plan
    
    except Exception as e:
        print(f"Error generating AI study plan: {str(e)}")
        
        # Return a basic fallback plan
        weeks_needed = 1
        if days_remaining:
            weeks_needed = max(1, days_remaining // 7)
        
        fallback_plan = {
            "overview": "Basic study plan to help you complete your courses",
            "recommendations": [
                "Focus on high-priority lessons first",
                "Spend at least 30 minutes per day on  [
                "Focus on high-priority lessons first",
                "Spend at least 30 minutes per day on your courses",
                "Take breaks between study sessions",
                "Review material regularly to reinforce learning"
            ],
            "weekly_plan": []
        }
        
        # Add basic weekly structure
        for week in range(weeks_needed):
            week_plan = {
                "week": week + 1,
                "focus": "Complete high-priority lessons",
                "days": []
            }
            
            # Add days
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                day_plan = {
                    "day": day,
                    "activities": [
                        {
                            "course": "Your course",
                            "lesson": "Next priority lesson",
                            "duration": 45,
                            "type": "lesson"
                        },
                        {
                            "course": "Your course",
                            "lesson": "Review previous material",
                            "duration": 15,
                            "type": "review"
                        }
                    ]
                }
                week_plan["days"].append(day_plan)
            
            fallback_plan["weekly_plan"].append(week_plan)
        
        return fallback_plan

