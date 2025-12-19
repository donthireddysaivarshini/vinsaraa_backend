from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem

# Cart Admin
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    readonly_fields = ('user', 'created_at', 'updated_at')


# Order Admin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'variant_label', 'price', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = ('id', 'user', 'total_amount', 'payment_status', 'order_status', 'created_at')
    list_filter = ('payment_status', 'order_status', 'created_at')
    search_fields = ('user__email', 'razorpay_order_id')
    readonly_fields = ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'created_at')
    fieldsets = (
        ('Order Info', {
            'fields': ('user', 'total_amount', 'created_at')
        }),
        ('Status', {
            'fields': ('payment_status', 'order_status'),  # ✅ EDITABLE
            'description': 'Update status here'
        }),
        ('Address & Contact', {
            'fields': ('shipping_address', 'phone')
        }),
        ('Razorpay Details', {
            'fields': ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature'),
            'classes': ('collapse',)
        }),
    )
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'variant_label', 'price', 'quantity')
    readonly_fields = ('order', 'product_name', 'variant_label', 'price', 'quantity')
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'variant', 'quantity')
    