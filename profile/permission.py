from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow the customer (owner)
    or an admin to access the customer or seller profiles.
    """

    def has_object_permission(self, request, view, obj):
        # Allow access only to the owner of the profile
        return request.user.is_staff or (
            request.user.customer or request.user.seller
            )


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow the customer or seller (owner)
    to access the customer's profile.
    """

    def has_object_permission(self, request, view, obj):
        # Allow access only to the owner of the profile
        return request.user and (
            obj.user.customer == request.user
            or obj.user.seller == request.user
        )
