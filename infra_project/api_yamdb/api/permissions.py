from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Custom permission for users with admin role."""

    message = 'Доступ только для администраторов и выше!'

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and (request.user.role == 'admin'
                     or request.user.is_superuser))


class IsAuthorOrReadOnlyPermission(permissions.BasePermission):
    """
    Access to safe points is allowed to everyone to
    the rest only user, admin and moderator.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return (obj.author == request.user
                    or request.user.role in ('admin', 'moderator')
                    or request.user.is_superuser)
        return False


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Access to safe points is allowed to everyone to
    the rest only admin.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.role == 'admin'
        return False
