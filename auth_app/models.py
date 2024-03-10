from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

from products_app.models import Product, Color

from .manager import UserManager


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, verbose_name="Пользователь", null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True, verbose_name="Номер телефона")
    email = models.CharField(max_length=50, unique=True, verbose_name="Почта", blank=True)
    status = models.CharField(max_length=50, default="user")
    user_image = models.ImageField(upload_to="media/user_image/", blank=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_administrator = models.BooleanField(default=False)
    date_joined = models.DateField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.user_image:
            self.user_image = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class AnonymousUser(models.Model):
    ip_address = models.GenericIPAddressField()
    session_key = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.session_key


class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_cart', null=True, blank=True)
    anonymous = models.ForeignKey(AnonymousUser, on_delete=models.CASCADE, related_name='anonymous_cart', null=True, blank=True)
    items = models.ManyToManyField(Product, through='CartItem')


class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='user_order', null=True, blank=True)
    anonymous = models.ForeignKey(AnonymousUser, on_delete=models.SET_NULL, related_name='anonymous_order', null=True,
                                  blank=True)
    op_sent = models.BooleanField(default=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    mobile = models.CharField(max_length=255, null=True, blank=True)
    items = models.ManyToManyField(Product, through="CartItem")
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True)
    color_quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])


class UserFavorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    anonymous = models.ForeignKey(AnonymousUser, on_delete=models.CASCADE, null=True, blank=True)
    fav_products = models.ManyToManyField(Product)
