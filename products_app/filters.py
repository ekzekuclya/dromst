from django_filters import BaseInFilter, CharFilter, NumberFilter
from django_filters.rest_framework import FilterSet

from .models import Product


class CharInField(BaseInFilter, CharFilter):
    pass


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class ProductFilter(FilterSet):
    title = CharInField(field_name="title", lookup_expr="in")
    colors = NumberInFilter(field_name="colors", lookup_expr="in")
    category = NumberInFilter(field_name="category", lookup_expr="in")
    subcategory = NumberInFilter(field_name="subcategory", lookup_expr="in")
    min_price = NumberFilter(field_name="price", lookup_expr="gte")
    max_price = NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ['title', 'colors', 'min_price', 'max_price', 'subcategory', 'category']