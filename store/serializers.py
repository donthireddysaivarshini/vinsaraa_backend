from rest_framework import serializers
from .models import Product, ProductVariant, Category, ProductImage, Coupon, SiteConfig

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'image', 'description')

class ProductImageSerializer(serializers.ModelSerializer):
    # This serializer is for internal use if needed
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'video', 'is_primary')

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ('id', 'size', 'stock', 'additional_price')

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    variants = ProductVariantSerializer(many=True, read_only=True)
    
    # Explicitly defining these as MethodFields to avoid "Field name not valid" error
    images = serializers.SerializerMethodField()
    videos = serializers.SerializerMethodField()
    
    # Mapped fields
    originalPrice = serializers.DecimalField(source='original_price', max_digits=10, decimal_places=2, required=False, allow_null=True)
    washCare = serializers.CharField(source='wash_care', required=False)
    isNew = serializers.BooleanField(source='is_new', required=False)
    
    class Meta:
        model = Product
        fields = (
            'id', 'title', 'slug', 'sku', 'description', 
            'price', 'originalPrice', 
            'fabric', 'color', 'washCare', 
            'category', 
            'images', # Matches the SerializerMethodField above
            'videos', # Matches the SerializerMethodField above
            'variants',
            'isNew', 'badge', 'is_active', 
            'disclaimer', 'manufacturer_name', 'manufacturer_address', 'country_of_origin'
        )

    def get_category(self, obj):
        return obj.category.name if obj.category else None

    def get_images(self, obj):
        request = self.context.get('request')
        # Filter only items that have an image
        media_items = obj.media.filter(image__isnull=False).exclude(image='')
        urls = []
        for item in media_items:
            if item.image:
                if request:
                    urls.append(request.build_absolute_uri(item.image.url))
                else:
                    urls.append(item.image.url)
        return urls

    def get_videos(self, obj):
        request = self.context.get('request')
        # Filter only items that have a video
        media_items = obj.media.filter(video__isnull=False).exclude(video='')
        urls = []
        for item in media_items:
            if item.video:
                if request:
                    urls.append(request.build_absolute_uri(item.video.url))
                else:
                    urls.append(item.video.url)
        return urls

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ('id', 'code', 'discount_type', 'value', 'min_order_value', 'valid_from', 'valid_to', 'active')

class SiteConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteConfig
        fields = ('id', 'shipping_flat_rate', 'shipping_free_above', 'tax_rate_percentage')