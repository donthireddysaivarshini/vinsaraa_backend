from rest_framework import serializers
from .models import Product, ProductVariant, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'image')

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ('id', 'size', 'color', 'sku', 'stock_quantity')

class ProductSerializer(serializers.ModelSerializer):
    # This ensures that when we fetch a Product, we get its Category and Variants too
    category = CategorySerializer(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'title', 'slug', 'description', 
            'price', 'image', 'category', 'variants'
        )