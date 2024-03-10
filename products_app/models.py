from django.db import models
from django.conf import settings


class ProductImage(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    image = models.ImageField(unique=True, upload_to="media/product_images/")

    def image_url(self):
        return settings.BASE_URL + self.image.url


class Color(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(unique=True, upload_to="media/colors/")

    def __str__(self):
        return self.name

    def image_url(self):
        return settings.BASE_URL + self.image.url


class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    colors = models.ManyToManyField(Color, blank=True)
    price = models.PositiveIntegerField(null=True, blank=True)
    discount = models.IntegerField()
    in_stock = models.BooleanField(default=True)
    product_class = models.CharField(max_length=255)
    responses = models.IntegerField(default=0, null=True, blank=True)
    category = models.ForeignKey("Category", on_delete=models.CASCADE, blank=True, null=True)
    subcategory = models.ManyToManyField("Subcategory", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name