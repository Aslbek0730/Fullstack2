from celery import shared_task
from .services import grade_essay_response, update_course_embedding, update_user_embedding

@shared_task
def grade_essay_response_task(response_id, answer_key=''):
    """
    Celery task to grade an essay response asynchronously.
    """
    grade_essay_response(response_id, answer_key)

@shared_task
def update_course_embedding_task(course_id):
    """
    Celery task to update a course embedding asynchronously.
    """
    from courses.models import Course
    course = Course.objects.get(id=course_id)
    update_course_embedding(course)

@shared_task
def update_user_embedding_task(user_id):
    """
    Celery task to update a user embedding asynchronously.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(id=user_id)
    update_user_embedding(user)

@shared_task
def update_all_course_embeddings():
    """
    Celery task to update all course embeddings.
    """
    from courses.models import Course
    courses = Course.objects.all()
    for course in courses:
        update_course_embedding_task.delay(course.id)

@shared_task
def update_all_user_embeddings():
    """
    Celery task to update all user embeddings.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    users = User.objects.all()
    for user in users:
        update_user_embedding_task.delay(user.id)

