from rest_framework.permissions import BasePermission


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_staff)
