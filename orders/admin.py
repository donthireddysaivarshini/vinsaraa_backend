from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem


# Cart Admin
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "updated_at")
    inlines = [CartItemInline]


# Order Admin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_amount", "order_status", "payment_status", "created_at")
    list_filter = ("order_status", "payment_status", "created_at")
    inlines = [OrderItemInline]

    readonly_fields = ("razorpay_order_id", "razorpay_payment_id", "razorpay_signature")

    actions = ["mark_as_shipped", "mark_as_delivered", "mark_as_cancelled"]

    def mark_as_shipped(self, request, queryset):
        queryset.update(order_status="shipped")

    mark_as_shipped.short_description = "Mark selected orders as Shipped"

    def mark_as_delivered(self, request, queryset):
        queryset.update(order_status="delivered")

    mark_as_delivered.short_description = "Mark selected orders as Delivered"

    def mark_as_cancelled(self, request, queryset):
        queryset.update(order_status="cancelled", payment_status="Failed")

    mark_as_cancelled.short_description = "Mark selected orders as Cancelled/Failed"