from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, Cart, CartItem

# Order Admin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'variant_label', 'price', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_email', 'total_amount', 'shipping_address_preview', 'payment_status_badge', 'order_status')
    list_filter = ('payment_status', 'order_status', 'created_at')
    search_fields = ('user__email', 'razorpay_order_id')
    
    # You can keep this if you still want row-by-row editing, 
    # but 'actions' below is the better way for bulk changes.
    list_editable = ('order_status',)
    
    # --- NEW CHANGE: Add Actions ---
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']
    
    # Add custom CSS for address column width
    class Media:
        css = {
            'all': ('admin/css/order_address.css',)
        }

    readonly_fields = (
        'user', 'total_amount', 'created_at',
        'shipping_address', 'phone',
        'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature'
    )
    
    fieldsets = (
        ('Order Info', {
            'fields': ('user', 'total_amount', 'created_at')
        }),
        ('Status', {
            'fields': ('payment_status', 'order_status'),
            'description': 'Change order status: Processing → Shipped → Delivered'
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
    
    # --- NEW CHANGE: Action Functions ---
    @admin.action(description='Mark selected orders as Processing')
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(order_status='Processing')
        self.message_user(request, f'{updated} orders marked as Processing.')

    @admin.action(description='Mark selected orders as Shipped')
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(order_status='Shipped')
        self.message_user(request, f'{updated} orders marked as Shipped.')

    @admin.action(description='Mark selected orders as Delivered')
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(order_status='Delivered')
        self.message_user(request, f'{updated} orders marked as Delivered.')
    # ------------------------------------

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "User"
    
    def shipping_address_preview(self, obj):
        """Display full address with proper formatting (multiple lines)"""
        if obj.shipping_address:
            # Split address into lines and format with HTML
            lines = obj.shipping_address.strip().split('\n')
            formatted_lines = [line.strip() for line in lines if line.strip()]
            
            # Create HTML with proper styling (Jazzmin compatible)
            html = '<div style="font-size: 12px; line-height: 1.5; color: #333; white-space: pre-wrap; word-wrap: break-word; max-width: 300px;">'
            for line in formatted_lines:
                html += f'{line}<br>'
            html += '</div>'
            
            return format_html(html)
        return '-'
    shipping_address_preview.short_description = "Address"
    
    def payment_status_badge(self, obj):
        """Display payment status with color"""
        if obj.payment_status == 'Paid':
            return format_html(
                '<span style="color: white; background-color: #28A745; padding: 5px 10px; border-radius: 3px; font-weight: bold;">✓ Paid</span>'
            )
        else:
            return format_html(
                '<span style="color: white; background-color: #FFA500; padding: 5px 10px; border-radius: 3px; font-weight: bold;">⏳ Pending</span>'
            )
    payment_status_badge.short_description = "Payment Status"
    
    def save_model(self, request, obj, form, change):
        """Save changes without blocking validation"""
        super().save_model(request, obj, form, change)
    
    def has_add_permission(self, request):
        """Disable adding orders from admin"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting orders"""
        return False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'variant_label', 'price', 'quantity')
    readonly_fields = ('order', 'product_name', 'variant_label', 'price', 'quantity')
    
    def has_add_permission(self, request):
        """Disable adding order items"""
        return False


# Hide Cart and CartItem - not needed in admin
admin.site.unregister(Cart) if Cart in admin.site._registry else None
admin.site.unregister(CartItem) if CartItem in admin.site._registry else None