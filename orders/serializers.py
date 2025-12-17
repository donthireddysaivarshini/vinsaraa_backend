from rest_framework import serializers

from .models import Cart, CartItem, Order, OrderItem
from store.models import ProductImage


class CartItemSerializer(serializers.ModelSerializer):
    product_title = serializers.ReadOnlyField(source="variant.product.title")
    product_slug = serializers.ReadOnlyField(source="variant.product.slug")
    size = serializers.ReadOnlyField(source="variant.size")
    price = serializers.DecimalField(
        source="price_per_unit", max_digits=10, decimal_places=2, read_only=True
    )
    image = serializers.SerializerMethodField()
    subtotal = serializers.DecimalField(
        source="total_price", max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = CartItem
        fields = (
            "id",
            "product_title",
            "product_slug",
            "size",
            "variant",
            "quantity",
            "price",
            "subtotal",
            "image",
        )

    def get_image(self, obj):
        # Fetch the primary image for the product
        image = ProductImage.objects.filter(
            product=obj.variant.product, is_primary=True
        ).first()
        if image:
            return image.image.url
        return None


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_cart_price = serializers.DecimalField(
        source="total_price", max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Cart
        fields = ("id", "user", "items", "total_cart_price", "updated_at")


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("id", "product_name", "variant_label", "price", "quantity")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "total_amount",
            "payment_status",
            "order_status",
            "shipping_address",
            "phone",
            "created_at",
            "items",
        )