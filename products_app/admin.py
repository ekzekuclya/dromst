from django.contrib import admin
from .models import Product, Category, Subcategory, Color, ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(ProductImage)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['id']