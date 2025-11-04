# accounts/permissions.py
from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    only admin access
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser

class IsStaff(permissions.BasePermission):
    """
    only staff access
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff

class IsUser(permissions.BasePermission):
    """
    only user access
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and not request.user.is_staff and not request.user.is_superuser
