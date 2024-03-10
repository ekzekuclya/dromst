from rest_framework import serializers
from .models import Product, Color, Category, Subcategory, ProductImage


class ColorSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):

        image_url = instance.image_url()
        res = super().to_representation(instance)
        res['image'] = image_url
        return res

    class Meta:
        model = Color
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = "__all__"


class ImageSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        image_url = instance.image_url()
        res = super().to_representation(instance)
        res['image'] = image_url
        return res

    class Meta:
        model = ProductImage
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        request = self.context.get('request')
        res = super().to_representation(instance)
        res['category'] = CategorySerializer(instance=instance.category).data
        res['subcategory'] = SubcategorySerializer(instance=instance.subcategory.all(), many=True).data
        res['colors'] = ColorSerializer(instance=instance.colors.all(), many=True).data
        res['images'] = ImageSerializer(instance=ProductImage.objects.filter(product=instance), many=True).data
        return res

    class Meta:
        model = Product
        exclude = ('responses',)
