from decimal import Decimal

from rest_framework import generics, status, views,permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from .models import Order
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes

from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer
from store.models import ProductVariant
from .serializers import OrderSerializer
from payments.razorpay_client import create_order as razorpay_create_order

from accounts.models import SavedAddress
from .serializers import SavedAddressSerializer


class UserOrdersView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items").order_by("-created_at")


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def order_status(request, pk):
    """
    GET /orders/<pk>/status/  -> returns simple status data used by frontend polling
    """
    try:
        order = Order.objects.prefetch_related("items").get(pk=pk, user=request.user)
    except Order.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)

    return Response({
        "order_id": order.id,
        "payment_status": order.payment_status,
        "order_status": order.order_status,
        "razorpay_order_id": order.razorpay_order_id,
        "razorpay_payment_id": order.razorpay_payment_id,
    })


@api_view(["PATCH"])
@permission_classes([permissions.IsAuthenticated])
def update_order_status(request, pk):
    """
    PATCH /orders/<pk>/update-status/
    Admin endpoint to update order status (only if payment is Paid).
    Body: {"order_status": "Shipped"} or {"order_status": "Delivered"}
    """
    try:
        order = Order.objects.get(pk=pk, user=request.user)
    except Order.DoesNotExist:
        return Response({"detail": "Order not found"}, status=404)
    
    # Check if user is staff (admin)
    if not request.user.is_staff:
        return Response(
            {"detail": "Permission denied. Admin only."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if payment is Paid before allowing status change
    if order.payment_status != "Paid":
        return Response(
            {
                "detail": "Cannot update order status while payment is Pending. "
                          "Status can only be changed after payment is marked as Paid."
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    new_status = request.data.get("order_status")
    valid_statuses = [choice[0] for choice in Order.ORDER_STATUS_CHOICES]
    
    if new_status not in valid_statuses:
        return Response(
            {
                "detail": f"Invalid order status. Must be one of: {valid_statuses}"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    order.order_status = new_status
    order.save()
    
    return Response({
        "order_id": order.id,
        "order_status": order.order_status,
        "message": "Order status updated successfully"
    }, status=status.HTTP_200_OK)

# --- CART VIEWS ---

class CartView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

class AddToCartView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        variant_id = request.data.get('variant_id')
        quantity = int(request.data.get('quantity', 1))

        cart, _ = Cart.objects.get_or_create(user=request.user)
        variant = get_object_or_404(ProductVariant, id=variant_id)

        if variant.stock < quantity:
            return Response({"error": "Not enough stock available"}, status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)
        
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

class RemoveCartItemView(views.APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        cart_item = get_object_or_404(CartItem, id=pk, cart__user=request.user)
        cart_item.delete()
        cart = Cart.objects.get(user=request.user)
        return Response(CartSerializer(cart).data)

#Adress
class SavedAddressListCreateView(generics.ListCreateAPIView):
    serializer_class = SavedAddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SavedAddress.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Enforce maximum 3 addresses per user
        existing_count = SavedAddress.objects.filter(user=self.request.user).count()
        if existing_count >= 3:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "You can save up to 3 addresses only."})

        # If the new address is set as default, unset others
        is_default = serializer.validated_data.get('is_default', False)
        if is_default:
            SavedAddress.objects.filter(user=self.request.user, is_default=True).update(is_default=False)

        serializer.save(user=self.request.user)

class SavedAddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SavedAddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SavedAddress.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        # If marked default, unset others
        is_default = serializer.validated_data.get('is_default', None)
        if is_default:
            SavedAddress.objects.filter(user=self.request.user, is_default=True).update(is_default=False)
        serializer.save()

    def perform_destroy(self, instance):
        # Prevent deletion if it's the only address? Allow deletion but ensure defaults
        was_default = instance.is_default
        user = self.request.user
        instance.delete()
        if was_default:
            # set any remaining address as default
            remaining = SavedAddress.objects.filter(user=user).first()
            if remaining:
                remaining.is_default = True
                remaining.save()

# --- CHECKOUT VIEW (This was missing!) ---

class CheckoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Checkout supports TWO modes:
        1) Client-side cart (recommended): frontend sends line items in request.data["items"]
        2) Legacy server cart: falls back to Cart model for the authenticated user
        """

        items_payload = request.data.get("items")

        order_line_items = []  # list of dicts: { "product_name", "size", "price_per_unit", "quantity" }
        total_amount = Decimal("0.00")

        if items_payload:
            # --- MODE 1: CLIENT-SIDE CART SENT FROM FRONTEND ---
            if not isinstance(items_payload, list):
                return Response(
                    {"error": "Invalid items format. Expected a list of items."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            for line in items_payload:
                sku = line.get("sku")
                size = line.get("size")
                quantity = int(line.get("quantity", 1) or 1)

                if not sku or not size:
                    return Response(
                        {"error": "Each item must include 'sku' and 'size'."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                variant = get_object_or_404(
                    ProductVariant,
                    product__sku=sku,
                    size=size,
                )

                if variant.stock < quantity:
                    return Response(
                        {
                            "error": f"Not enough stock for {variant.product.title} ({size})"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                price_per_unit = variant.product.price + variant.additional_price
                line_total = price_per_unit * quantity
                total_amount += line_total

                order_line_items.append(
                    {
                        "product_name": variant.product.title,
                        "size": size,
                        "price_per_unit": price_per_unit,
                        "quantity": quantity,
                    }
                )
        else:
            # --- MODE 2: SERVER-SIDE CART (if ever used) ---
            try:
                cart = Cart.objects.get(user=request.user)
                if cart.items.count() == 0:
                    return Response(
                        {"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
                    )
            except Cart.DoesNotExist:
                return Response(
                    {"error": "No cart found for this user"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Use server cart totals
            total_amount = cart.total_price

            for item in cart.items.all():
                price_per_unit = (
                    item.variant.product.price + item.variant.additional_price
                )
                order_line_items.append(
                    {
                        "product_name": item.variant.product.title,
                        "size": item.variant.size,
                        "price_per_unit": price_per_unit,
                        "quantity": item.quantity,
                    }
                )

            # We'll clear the server cart after creating the order (see below)
            cart_to_clear = cart

        # 2. Create the Order
        address = request.data.get('address', '')
        apartment = request.data.get('apartment', '')
        city = request.data.get('city', '')
        state = request.data.get('state', '')
        zip_code = request.data.get('zip_code', '')
        country = request.data.get('country', '')
        phone = request.data.get('phone', '')
        shipping_address = f"{address}\n{apartment}\n{city}, {state} {zip_code}\n{country}".strip()

        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            phone=phone,
            total_amount=total_amount,
            payment_status='Pending',
            order_status='Processing'  # Explicitly set to Processing, not pending
        )

        # 3. Move items into OrderItems (from whichever mode built order_line_items)
        for line in order_line_items:
            OrderItem.objects.create(
                order=order,
                product_name=line["product_name"],
                variant_label=f"Size: {line['size']}",
                price=line["price_per_unit"],
                quantity=line["quantity"],
            )

        # CRITICAL: Stock is NOT deducted here!
        # Stock will be deducted only after payment verification succeeds
        # (see payments.VerifyPaymentView)

        # 4. Clear server-side cart (whether we used it or not)
        # This ensures cart is always empty after checkout
        try:
            user_cart = Cart.objects.get(user=request.user)
            user_cart.items.all().delete()  # Clear all cart items
        except Cart.DoesNotExist:
            pass  # No cart to clear, that's fine

        # 6. Create Razorpay Order (amount in rupees → paise handled in utility)
        try:
            razorpay_order = razorpay_create_order(total_amount, currency="INR")
        except Exception as exc:
            # If Razorpay order creation fails, surface a clear error.
            return Response(
                {"error": "Failed to create Razorpay order", "details": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Save Razorpay order id on our Order model
        order.razorpay_order_id = razorpay_order.get("id")
        order.save(update_fields=["razorpay_order_id"])

        # 7. Respond with data needed by frontend Razorpay widget
        return Response(
            {
                "id": order.id,
                "razorpay_order_id": order.razorpay_order_id,
                "amount": razorpay_order.get("amount"),  # in paise
                "currency": razorpay_order.get("currency", "INR"),
                "key": getattr(settings, "RAZORPAY_KEY_ID", ""),
                "order_status": order.order_status,
                "payment_status": order.payment_status,
            },
            status=status.HTTP_201_CREATED,
        )