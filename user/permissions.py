from rest_framework import permissions


class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'
class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.role == 'admin'
