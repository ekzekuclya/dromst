from django.contrib.auth import authenticate
from rest_framework import status, viewsets
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from .serializers import LoginSerializer, RegUserSerializer, OrderSerializer, CartItemSerializer, \
    FavoriteProductSerializer
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import CartItem, Cart, UserFavorite, Order
from .permissions import OrderPermission
from .utils import save_anonymous


class RegUserViewSet(CreateAPIView):
    serializer_class = RegUserSerializer
    permission_classes = [AllowAny]


class LoginAPIView(CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                access = AccessToken.for_user(user)
                return Response({
                    'message': 'Пользователь успешно аутентифицирован.',
                    "status": status.HTTP_200_OK,
                    "refresh_token": str(refresh),
                    "access_token": str(access)
                })
            return Response({'message': 'Ошибка аутентификации. Пожалуйста, проверьте введенные данные.'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyCartViewSet(ListAPIView):
    serializer_class = CartItemSerializer
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=user)
            qs = CartItem.objects.filter(cart=cart)
            return qs
        else:
            anonymous = save_anonymous(self.request)
            if anonymous is not None:
                cart, created = Cart.objects.get_or_create(anonymous=anonymous)
                qs = CartItem.objects.filter(cart=cart)
                return qs
            else:
                return Response({"detail": "NO SESSION"}, status=status.HTTP_404_NOT_FOUND)


class CartActionViewSet(APIView):
    def post(self, request, pk):
        cart_item = CartItem.objects.get(id=pk)
        cart_item.delete()
        return Response({"detail": "Item deleted"}, status=status.HTTP_200_OK)


class MyFavoriteView(viewsets.ViewSet):
    queryset = UserFavorite.objects.all()
    serializer_class = FavoriteProductSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['GET'], url_path="my_favorites")
    def get_favorite_products(self, request):
        user = request.user
        if user.is_authenticated:
            favorite, created = UserFavorite.objects.get_or_create(user=user)
            return Response(FavoriteProductSerializer(favorite).data, status=status.HTTP_200_OK)
        else:
            anonymous = save_anonymous(request)
            if anonymous is not None:
                favorite, created = UserFavorite.objects.get_or_create(anonymous=anonymous)
                return Response(FavoriteProductSerializer(favorite).data, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "NO SESSION"}, status=status.HTTP_404_NOT_FOUND)


class OrderViewSet(viewsets.ViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [OrderPermission]

    @action(detail=False, methods=['post'], url_path='new_order')
    def order_items(self, request):
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            if len(cart.items.all()) < 1:
                return Response({"detail": "no products in cart"}, status=status.HTTP_400_BAD_REQUEST)
            order = Order.objects.create(user=request.user)
            cart_item = CartItem.objects.filter(cart=cart)

            for i in cart_item:
                order_item, created = CartItem.objects.get_or_create(order=order, product=i.product, quantity=i.quantity)
                if i.color:
                    order_item.color = i.color
                    order_item.save(update_fields=['color'])
            if request.data.get('name'):
                order.name = request.data['name']
            if request.data.get('mobile'):
                order.mobile = request.data['mobile']
            order.save()

            cart.items.clear()
            return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
        else:
            anonymous = save_anonymous(self.request)
            if anonymous is not None:
                cart, created = Cart.objects.get_or_create(anonymous=anonymous)
                if len(cart.items.all()) < 1:
                    return Response({"detail": "no products in cart"}, status=status.HTTP_400_BAD_REQUEST)
                cart_item = CartItem.objects.filter(cart=cart)
                order = Order.objects.create(anonymous=anonymous)
                for i in cart_item:
                    order_item, created = CartItem.objects.get_or_create(order=order, product=i.product, quantity=i.quantity, color=i.color)

                if request.data.get('name'):
                    order.name = request.data['name']
                if request.data.get('mobile'):
                    order.mobile = request.data['mobile']
                order.save()

                cart.items.clear()
                return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "NO SESSION"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['GET'], url_path='all_orders')
    def get_all_orders(self, request):
        orders = Order.objects.all()
        return Response(OrderSerializer(orders, many=True).data, status=status.HTTP_200_OK)