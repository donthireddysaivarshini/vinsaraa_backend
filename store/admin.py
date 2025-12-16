from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, ProductVariant, Coupon, SiteConfig

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'video', 'is_primary', 'preview')
    readonly_fields = ['preview']

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.image.url)
        elif obj.video:
            return format_html('<span>Video Uploaded</span>')
        return ""

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductVariantInline]
    
    list_display = ('title', 'sku', 'category', 'price', 'is_new', 'is_active', 'image_preview')
    list_filter = ('category', 'is_active', 'is_new', 'created_at')
    search_fields = ('title', 'sku', 'description')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('category', 'title', 'slug', 'sku', 'is_active', 'is_new', 'badge')
        }),
        ('Pricing', {
            'fields': ('price', 'original_price')
        }),
        ('Product Details', {
            'fields': ('description', 'fabric', 'color', 'wash_care') 
            # Note: video removed from here, it is now in the inline below
        }),
        ('Accordions / Legal', {
            'fields': ('disclaimer', 'manufacturer_name', 'manufacturer_address', 'country_of_origin')
        }),
    )

    def image_preview(self, obj):
        # Find first item with an image
        first_media = obj.media.filter(image__isnull=False).exclude(image='').first()
        if first_media and first_media.image:
            return format_html('<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px;" />', first_media.image.url)
        return "-"
    image_preview.short_description = "Image"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'value', 'active', 'valid_to')
    list_filter = ('active', 'discount_type')

admin.site.register(SiteConfig)