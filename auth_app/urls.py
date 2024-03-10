from django.urls import path, include

from rest_framework_nested import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView
)
from .views import RegUserViewSet, LoginAPIView, OrderViewSet, MyCartViewSet, MyFavoriteView, CartActionViewSet

router = routers.DefaultRouter()
router.register('orders', OrderViewSet, basename='orders')
router.register('favorite', MyFavoriteView, basename='favorite')


urlpatterns = [
    path('cart/<int:pk>/remove_item_cart/', CartActionViewSet.as_view(), name='remove-item-card'),
    path('cart/', MyCartViewSet.as_view()),
    path('', include(router.urls)),
    path('signup/', RegUserViewSet.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]