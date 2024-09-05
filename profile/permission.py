from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow the customer (owner)
    or an admin to access the customer or seller profiles.
    """

    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'is_staff') and request.user.is_staff:
            return True

        # Check if the user is the owner of the profile
        # (either customer or seller)
        is_customer = hasattr(
            request.user, 'customer') and request.user.customer == obj
        is_seller = hasattr(
            request.user, 'seller') and request.user.seller == obj

        return is_customer or is_seller


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


class IsCustomerOrAdminForRelatedObjects(permissions.BasePermission):
    """
    Custom permission to allow only the customer (owner) or
      admin to access Cart, CartItems, Orders, and OrderItems.
    """

    def has_object_permission(self, request, view, obj):
        # Allow access to admin users
        if request.user.is_staff:
            return True

        # If the user is associated with a Customer
        if hasattr(request.user, 'customer'):
            # Check if the object is associated with the Customer
            if hasattr(obj, 'customer'):  # For Cart and Order
                return obj.customer == request.user.customer
            elif hasattr(obj, 'cart') and hasattr(obj.cart, 'customer'):
                return obj.cart.customer == request.user.customer
            elif hasattr(obj, 'order') and hasattr(obj.order, 'customer'):
                return obj.order.customer == request.user.customer

        # If not an admin or owner, deny access


class IsSellerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow the seller (owner) or an admin
    to access or modify the seller profile.
    """

    def has_object_permission(self, request, view, obj):
        # Allow access to superusers (admin)
        if request.user.is_staff:
            return True

        # Allow access to the seller who owns the profile
        return hasattr(request.user, 'seller') and request.user.seller == obj
