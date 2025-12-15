from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, ProductVariant, Coupon, SiteConfig

# --- Inline Classes (For editing Images/Variants inside Product Page) ---
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.image.url)
        return ""

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

# --- Main Product Admin ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductVariantInline]
    
    # Columns to show in the list view
    list_display = ('title', 'sku', 'category', 'price', 'is_new', 'is_active', 'image_preview')
    
    # Filters on the right side
    list_filter = ('category', 'is_active', 'is_new', 'created_at')
    
    # Search bar
    search_fields = ('title', 'sku', 'description')
    
    # Organized Layout
    fieldsets = (
        ('Basic Info', {
            'fields': ('category', 'title', 'slug', 'sku', 'is_active', 'is_new', 'badge')
        }),
        ('Pricing', {
            'fields': ('price', 'original_price')
        }),
        ('Product Details', {
            'fields': ('description', 'fabric', 'color', 'wash_care', 'video_url')
        }),
    )

    def image_preview(self, obj):
        first_image = obj.images.filter(is_primary=True).first() or obj.images.first()
        if first_image and first_image.image:
            return format_html('<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px;" />', first_image.image.url)
        return "-"
    image_preview.short_description = "Image"

# --- Other Admins ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'value', 'active', 'valid_to')
    list_filter = ('active', 'discount_type')

# Config is unchanged, just registered
admin.site.register(SiteConfig)