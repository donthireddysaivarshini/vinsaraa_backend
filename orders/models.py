from django.db import models
from django.conf import settings
from store.models import ProductVariant

# --- CART MODELS (Temporary Basket) ---
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def price_per_unit(self):
        """Calculate price per unit (product price + variant additional price)"""
        return self.variant.product.price + self.variant.additional_price
    
    @property
    def total_price(self):
        return self.price_per_unit * self.quantity

# --- ORDER MODELS (Final Receipt) ---
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    
    # Shipping Info (Simplified for now)
    shipping_address = models.TextField()
    phone = models.CharField(max_length=20)
    
    # Payment Info
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, default='Pending')
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Razorpay Integration Fields
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True, help_text="Razorpay Order ID")
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True, help_text="Razorpay Payment ID")
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True, help_text="Razorpay Signature")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.email}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255) # Snapshot of name at time of purchase
    variant_label = models.CharField(max_length=255) # e.g. "Size: M, Color: Red"
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"