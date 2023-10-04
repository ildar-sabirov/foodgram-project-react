from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_staff)


class IsAuthorOfRecipe(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
