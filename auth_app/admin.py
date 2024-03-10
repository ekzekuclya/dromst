from django.contrib import admin
from .models import CustomUser, Cart, Order, AnonymousUser, CartItem, UserFavorite


@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    list_display = ['id']


@admin.register(AnonymousUser)
class AnonymousUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'ip_address']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id']


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id']
