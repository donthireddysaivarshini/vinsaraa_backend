from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Selling Price")
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="MRP (Strikethrough price)")
    
    # Product Details
    fabric = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=50, blank=True)
    wash_care = models.CharField(max_length=100, blank=True, default="Dry clean only")
    
    # Accordion Fields
    disclaimer = models.TextField(blank=True, default="Product color may slightly vary due to photographic lighting or your device settings.")
    manufacturer_name = models.CharField(max_length=100, blank=True, default="VINSARAA")
    manufacturer_address = models.TextField(blank=True, default="Andhra Pradesh, India")
    country_of_origin = models.CharField(max_length=50, default="India")

    # Flags & Badges
    is_active = models.BooleanField(default=True)
    is_new = models.BooleanField(default=False, verbose_name="New Arrival")
    badge = models.CharField(max_length=20, blank=True, null=True, help_text="e.g., 'FS' (Free Shipping), 'BESTSELLER'")
    
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='media') # Renamed related_name to 'media' for clarity
    
    # Now supports Image OR Video
    image = models.ImageField(upload_to='products/', blank=True, null=True, help_text="Upload Image")
    video = models.FileField(upload_to='product_videos/', blank=True, null=True, help_text="Upload Video (MP4)")
    
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.title}"
    class Meta:
        verbose_name = "Product Image/Video"
        verbose_name_plural = "Product Images/Videos"

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.CharField(max_length=10) # S, M, L, XL
    stock = models.IntegerField(default=0)
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        unique_together = ('product', 'size') 

    def __str__(self):
        return f"{self.product.title} - {self.size}"

class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    )
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    usage_limit = models.IntegerField(default=100)
    uses_count = models.IntegerField(default=0)

    def __str__(self):
        return self.code

class SiteConfig(models.Model):
    shipping_flat_rate = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    shipping_free_above = models.DecimalField(max_digits=10, decimal_places=2, default=2000.00)
    tax_rate_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=18.00) 
    
    def __str__(self):
        return "Miscellaneous Charges Configuration"

    class Meta:
        verbose_name = "Miscellaneous Charges"
        verbose_name_plural = "Miscellaneous Charges"