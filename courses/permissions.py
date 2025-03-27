from rest_framework import permissions

class IsInstructorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow instructors to edit their courses.
    """
    
    def has_permission(self, request, view):
        # Allow GET, HEAD, OPTIONS requests
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for authenticated users
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, OPTIONS requests
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for the instructor
        if hasattr(obj, 'instructor'):
            return obj.instructor == request.user
        elif hasattr(obj, 'course'):
            return obj.course.instructor == request.user
        
        return False

class IsEnrolledOrInstructor(permissions.BasePermission):
    """
    Permission to only allow access to users enrolled in a course or the instructor.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Check if user is instructor
        if hasattr(obj, 'course'):
            if obj.course.instructor == user:
                return True
        elif hasattr(obj, 'lesson') and hasattr(obj.lesson, 'course'):
            if obj.lesson.course.instructor == user:
                return True
        
        # Check if user is enrolled
        course = None
        if hasattr(obj, 'course'):
            course = obj.course
        elif hasattr(obj, 'lesson') and hasattr(obj.lesson, 'course'):
            course = obj.lesson.course
        
        if course:
            return course.enrollments.filter(user=user).exists()
        
        return False

