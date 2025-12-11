from django.contrib import admin
from .models import Category, Product, ProductImage, ProductVariant, Coupon, SiteConfig

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductVariantInline]
    list_display = ('title', 'category', 'price', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'sku')

admin.site.register(Category)
admin.site.register(Coupon)
admin.site.register(SiteConfig)