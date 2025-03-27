from django.db.models.signals import post_save
from django.dispatch import receiver
from courses.models import Course
from django.contrib.auth import get_user_model
from .tasks import update_course_embedding_task, update_user_embedding_task

User = get_user_model()

@receiver(post_save, sender=Course)
def update_course_embedding_on_save(sender, instance, created, **kwargs):
    """
    Update course embedding when a course is created or updated.
    """
    update_course_embedding_task.delay(instance.id)

@receiver(post_save, sender=User)
def update_user_embedding_on_save(sender, instance, created, **kwargs):
    """
    Update user embedding when a user is created or updated.
    """
    update_user_embedding_task.delay(instance.id)

