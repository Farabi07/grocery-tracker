from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """
    Custom permission to allow only Admin users to access certain views.
    """
    def has_permission(self, request, view):
        return request.user.role == 'admin'


class IsEmployee(BasePermission):
    """
    Custom permission to allow only Employee users to access certain views.
    """
    def has_permission(self, request, view):
        return request.user.role == 'employee'
