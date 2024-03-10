from rest_framework import permissions


class OrderPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == "order_items":
            return True
        if view.action == "get_all_orders":
            if request.user.is_authenticated:
                if request.user.is_administator:
                    return True
            return False
