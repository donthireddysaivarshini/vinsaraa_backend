from rest_framework import serializers
from .models import Product, ProductVariant, Category, ProductImage

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'image')

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'is_primary')

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ('id', 'size', 'stock', 'additional_price')

class ProductSerializer(serializers.ModelSerializer):
    # Flattening data for Frontend Compatibility
    category = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'title', 'slug', 'sku', 'description', 
            'price', 'original_price', 
            'fabric', 'color', 'wash_care', 
            'category', 'images', 'sizes',
            'is_new', 'badge', 'is_active'
        )

    # 1. Return category name (or slug) instead of just ID, or full object
    def get_category(self, obj):
        return obj.category.name if obj.category else None

    # 2. Return list of image URLs: ["/media/img1.jpg", "/media/img2.jpg"]
    def get_images(self, obj):
        request = self.context.get('request')
        images = obj.images.all()
        if request:
            return [request.build_absolute_uri(img.image.url) for img in images]
        return [img.image.url for img in images]

    # 3. Return list of sizes: ["S", "M", "L"]
    def get_sizes(self, obj):
        return [variant.size for variant in obj.variants.all()]