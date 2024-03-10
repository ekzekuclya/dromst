from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status, generics
from rest_framework.response import Response
from .filters import ProductFilter
from .models import Product, Color, Category, Subcategory, ProductImage
from .permissions import ProductPermission, DefaultPermission
from .serializers import ProductSerializer, ColorSerializer, CategorySerializer, SubcategorySerializer, ImageSerializer
from datetime import datetime, timedelta
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404

from auth_app.models import CartItem, Cart, AnonymousUser, UserFavorite
from auth_app.serializers import CartItemSerializer, CartSerializer, FavoriteProductSerializer
from auth_app.utils import save_anonymous


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related('category').prefetch_related('colors')
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    permission_classes = [ProductPermission]
    ordering = ['id']
    search_fields = ['title', 'brand', 'price']

    @action(detail=True, methods=['POST'], url_path='favorite_add')
    def add_to_favorite(self, request, pk):
        product = Product.objects.filter(id=pk).first()
        if request.user.is_authenticated:
            favorite, created = UserFavorite.objects.get_or_create(user=request.user)
            if product not in favorite.fav_products.all():
                favorite.fav_products.add(product)
            elif product in favorite.fav_products.all():
                favorite.fav_products.remove(product)
            return Response(FavoriteProductSerializer(favorite).data, status=status.HTTP_200_OK)
        elif not request.user.is_authenticated:
            anonymous = save_anonymous(request)
            if anonymous is not None:
                favorite, created = UserFavorite.objects.get_or_create(anonymous=anonymous)
                if product not in favorite.fav_products.all():
                    favorite.fav_products.add(product)
                elif product in favorite.fav_products.all():
                    favorite.fav_products.remove(product)
                return Response(FavoriteProductSerializer(favorite).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='similar')
    def get_similar_products(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        similar = Product.objects.filter(category=product.category).exclude(id=pk)
        return Response(ProductSerializer(similar, many=True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path='popular')
    def get_popular_products(self, request):
        popular = Product.objects.all().order_by('-responses')
        return Response(ProductSerializer(popular, many=True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path="new")
    def get_new_products(self, request):

        last_month_start = timezone.now() - timedelta(days=30)
        last_month_products = Product.objects.filter(created_at__gte=last_month_start)
        serializer = ProductSerializer(last_month_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        last_view_time_str = request.session.get(f'product_view_{instance.id}', None)

        if last_view_time_str is None or (
                timezone.now() - datetime.strptime(last_view_time_str, "%Y-%m-%d %H:%M:%S.%f%z")).seconds >= 3600:
            instance.responses += 1
            instance.save()
            serialized_time = str(timezone.now())
            request.session[f'product_view_{instance.id}'] = serialized_time

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'], url_path='add')
    def add_to_cart(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        color_id = request.data.get("color")
        quantity = int(request.data.get("quantity", 1))
        if not color_id and len(product.colors.all()) >= 1:
            return Response({"detail": "Please choose color"}, status=status.HTTP_400_BAD_REQUEST)
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            anonymous = save_anonymous(request)
            if anonymous is not None:
                print("ANONYMOUS 110", anonymous)
                cart, created = Cart.objects.get_or_create(anonymous=anonymous)
        if color_id:
            color = get_object_or_404(Color, pk=color_id)
            if color not in product.colors.all():
                return Response({"detail": "Color not found"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            color = None

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, color=color)
        if not created:
            if quantity > 1:
                cart_item.quantity = quantity
                cart_item.color_quantity = quantity
                cart_item.save(update_fields=['quantity', 'color_quantity'])
            else:
                cart_item.quantity += quantity
                cart_item.color_quantity += quantity
                cart_item.save(update_fields=['quantity', 'color_quantity'])
        else:
            cart_item.quantity = quantity
            cart_item.color_quantity = quantity
            cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path='remove')
    def remove_from_cart(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        color_id = request.data.get("color")

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            anonymous = save_anonymous(request)
            if anonymous is not None:
                cart, created = Cart.objects.get_or_create(anonymous=anonymous)
        if color_id:
            color = get_object_or_404(Color, pk=color_id)
        else:
            color = None

        cart_item = CartItem.objects.filter(cart=cart, product=product, color=color).first()

        if cart_item:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.color_quantity -= 1
                cart_item.save(update_fields=['quantity', 'color_quantity'])
            else:
                cart_item.delete()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name']
    permission_classes = [DefaultPermission]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name']
    permission_classes = [DefaultPermission]

    def retrieve(self, request, *args, **kwargs):
        category = self.get_object()
        serializer = ProductSerializer(Product.objects.filter(category=category), many=True).data
        return Response(serializer)


class SubcategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.all().select_related('category')
    serializer_class = SubcategorySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name']
    permission_classes = [DefaultPermission]

    def retrieve(self, request, *args, **kwargs):
        subcategory = self.get_object()
        serializer = ProductSerializer(Product.objects.filter(subcategory=subcategory), many=True).data
        return Response(serializer)


class ImageCreateView(generics.CreateAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [DefaultPermission]


class ImageListView(generics.ListAPIView):
    serializer_class = ImageSerializer

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return ProductImage.objects.filter(product_id=product_id)
