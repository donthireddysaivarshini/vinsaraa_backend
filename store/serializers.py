from rest_framework import serializers
from .models import Product, ProductVariant, Category, ProductImage, Coupon, SiteConfig

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'image', 'description')

class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'is_primary')
    
    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ('id', 'size', 'stock', 'additional_price')

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    variants = ProductVariantSerializer(many=True, read_only=True)
    
    originalPrice = serializers.DecimalField(source='original_price', max_digits=10, decimal_places=2, required=False, allow_null=True)
    washCare = serializers.CharField(source='wash_care', required=False)
    isNew = serializers.BooleanField(source='is_new', required=False)

    class Meta:
        model = Product
        fields = (
            'id', 'title', 'slug', 'sku', 'description', 
            'price', 'originalPrice', 
            'fabric', 'color', 'washCare', 
            'category', 'images', 'variants',
            'isNew', 'badge', 'is_active'
        )

    def get_category(self, obj):
        return obj.category.name if obj.category else None

    def get_images(self, obj):
        request = self.context.get('request')
        images = obj.images.all()
        if request:
            return [request.build_absolute_uri(img.image.url) for img in images]
        return [img.image.url for img in images]

    def get_sizes(self, obj):
        return [variant.size for variant in obj.variants.all()]

# NEW: Coupon Serializer
class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ('id', 'code', 'discount_type', 'value', 'min_order_value', 'valid_from', 'valid_to', 'active')

# NEW: Site Config Serializer
class SiteConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteConfig
        fields = ('id', 'shipping_flat_rate', 'shipping_free_above', 'tax_rate_percentage')