from .views import ProductViewSet, ColorViewSet, CategoryViewSet, SubcategoryViewSet, ImageCreateView, ImageListView
from django.urls import path, include
from rest_framework_nested import routers

router = routers.DefaultRouter()


router.register('categories', CategoryViewSet, basename='categories')
router.register('subcategories', SubcategoryViewSet, basename='subcategories')
router.register('colors', ColorViewSet, basename='colors')
router.register('products', ProductViewSet, basename='products')
product_router = routers.NestedSimpleRouter(router, r'products', lookup='product')


urlpatterns = [
    path('image/create/', ImageCreateView.as_view(), name='image_create'),
    path('image/list/<int:product_id>/', ImageListView.as_view(), name='image_list'),
    path('', include(router.urls)),
    path('', include(product_router.urls)),
]