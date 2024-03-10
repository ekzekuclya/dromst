import re

from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import CustomUser, Cart, CartItem, Order, UserFavorite
from products_app.serializers import ProductSerializer, ColorSerializer


class CartSerializer(serializers.ModelSerializer):
    quantity = serializers.SerializerMethodField

    def get_quantity(self, obj):
        return obj.quantity

    def to_representation(self, instance):
        res = super().to_representation(instance)
        res['items'] = ProductSerializer(instance=instance.items.all(), many=True).data
        return res

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items']


class FavoriteProductSerializer(serializers.ModelSerializer):
    fav_products = ProductSerializer(many=True)

    class Meta:
        model = UserFavorite
        fields = ['user', 'anonymous', 'fav_products']



class RegUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        # fields = ('email', 'password', 'password2')
        exclude = ('username', 'user_image')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})

        if not 8 <= len(attrs['password']) <= 14:
            raise serializers.ValidationError({"password": "Пароль не может быть меньше 8ми символов и больше 14и"})

        if not re.search(r'\d', attrs['password']) or not re.search(r'[a-zA-Z]', attrs['password']):
            raise serializers.ValidationError({"password": "Пароль должен быть на латинице и содержать число"})

        if not re.match(r'^[a-zA-Z0-9!@#$%^&*()_\-+=]+$', attrs['password']):
            raise serializers.ValidationError({"password": "Недопустимый символ !@#$%^&*()_"})

        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create(
            email=validated_data['email'],
        )
        user.username = "user" + str(user.id)
        user.last_login = timezone.now()
        user.set_password(validated_data['password'])
        user.save()
        # request = self.context.get('request')
        # ip = get_client_ip(request)
        # save_signup_info.delay(user.id, ip)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    color = ColorSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'color']


class OrderSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        res = super().to_representation(instance)
        order = Order.objects.get(id=instance.id)
        res['items'] = CartItemSerializer(instance=CartItem.objects.filter(order=order), many=True).data
        return res

    class Meta:
        model = Order
        fields = "__all__"
