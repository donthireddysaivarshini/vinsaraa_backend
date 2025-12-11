from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2) # Base Price
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    video_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.title}"

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.CharField(max_length=10) # S, M, L, XL
    sku = models.CharField(max_length=50, unique=True)
    stock = models.IntegerField(default=0)
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # If XL costs more
    
    class Meta:
        unique_together = ('product', 'size') # Prevent duplicate sizes for same product

    def __str__(self):
        return f"{self.product.title} - {self.size}"

class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    )
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2) # 10% or ₹100
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    usage_limit = models.IntegerField(default=100)
    uses_count = models.IntegerField(default=0)

    def __str__(self):
        return self.code

# [cite_start]SITE CONFIG: Stores Global Tax & Shipping settings [cite: 22, 30]
class SiteConfig(models.Model):
    shipping_flat_rate = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    shipping_free_above = models.DecimalField(max_digits=10, decimal_places=2, default=2000.00)
    tax_rate_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=18.00) # 18% GST
    
    def __str__(self):
        return "Site Configuration (Edit here to change global charges)"

    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"