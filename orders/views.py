from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer
from store.models import ProductVariant

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


# --- CHECKOUT VIEW (This was missing!) ---

class CheckoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1. Get the user's cart
        try:
            cart = Cart.objects.get(user=request.user)
            if cart.items.count() == 0:
                 return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({"error": "No cart found"}, status=status.HTTP_404_NOT_FOUND)

        # 2. Calculate Total
        total_amount = cart.total_price 
        
        # 3. Create the Order
        shipping_address = request.data.get('address', 'No address provided')
        phone = request.data.get('phone', '')

        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            phone=phone,
            total_amount=total_amount,
            payment_status='Pending'
        )

        # 4. Move items from Cart to Order
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product_name=item.variant.product.title,
                variant_label=f"Size: {item.variant.size}",
                price=item.price_per_unit,
                quantity=item.quantity
            )
            
            # Reduce Stock
            item.variant.stock -= item.quantity
            item.variant.save()

        # 5. Clear the Cart
        cart.items.all().delete()

        return Response({
            "message": "Order placed successfully", 
            "order_id": order.id
        }, status=status.HTTP_201_CREATED)