from rest_framework import permissions


class ProductPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        if view.action in ["add_to_cart", "remove_from_cart", "add_to_favorite"]:
            return True
        else:
            if request.method == "POST":
                if request.user.is_authenticated:
                    if request.user.is_administrator:
                        return True
                return False
            return False


class DefaultPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        if request.method == "POST":
            if request.user.is_authenticated:
                if request.user.is_administrator:
                    return True
            return False
        return False
