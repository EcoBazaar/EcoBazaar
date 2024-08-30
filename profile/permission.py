from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow the customer (owner)
    or an admin to access the customer's profile.
    """

    def has_object_permission(self, request, view, obj):
        # Allow access only to the owner of the profile or an admin
        return request.user and (
            obj.customer.user == request.user or request.user.is_staff)


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow the customer (owner)
    to access the customer's profile.
    """

    def has_object_permission(self, request, view, obj):
        # Allow access only to the owner of the profile
        return request.user and (obj.customer.user == request.user)
