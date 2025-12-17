from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order, OrderItem
from payments.razorpay_client import verify_payment_signature
from store.models import ProductVariant


class VerifyPaymentView(APIView):
    """
    Verifies Razorpay payment and, if valid, safely deducts stock.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        razorpay_signature = request.data.get("razorpay_signature")

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return Response(
                {"error": "Missing Razorpay payment details"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. Verify signature with Razorpay
        try:
            verify_payment_signature(
                razorpay_order_id=razorpay_order_id,
                razorpay_payment_id=razorpay_payment_id,
                razorpay_signature=razorpay_signature,
            )
        except Exception as exc:
            # Signature invalid or Razorpay error
            return Response(
                {"error": "Payment verification failed", "details": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2. Atomic transaction for order + stock update
        with transaction.atomic():
            order = (
                Order.objects.select_for_update()
                .select_related("user")
                .prefetch_related("items")
                .filter(razorpay_order_id=razorpay_order_id, user=request.user)
                .first()
            )

            if not order:
                return Response(
                    {"error": "Order not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # If already paid, treat as idempotent success
            if order.payment_status.lower() == "paid":
                return Response(
                    {
                        "success": True,
                        "message": "Payment already verified",
                        "order_id": order.id,
                    },
                    status=status.HTTP_200_OK,
                )

            # Save payment identifiers
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.payment_status = "Paid"
            order.order_status = "paid"

            # 3. Deduct stock with row-level locks
            for item in order.items.all():
                # Our OrderItem stores product_name and variant_label ("Size: M")
                # We infer the variant via product title + size.
                size = None
                if item.variant_label and ":" in item.variant_label:
                    # "Size: M" → "M"
                    size = item.variant_label.split(":", 1)[1].strip()

                if not size:
                    raise ValueError("Invalid variant label on order item.")

                variant = (
                    ProductVariant.objects.select_for_update()
                    .filter(product__title=item.product_name, size=size)
                    .first()
                )

                if not variant:
                    return Response(
                        {
                            "error": "Variant not found for order item",
                            "item": item.product_name,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if variant.stock < item.quantity:
                    return Response(
                        {
                            "error": "Out of stock for one or more items",
                            "item": item.product_name,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                variant.stock -= item.quantity
                variant.save()

            order.save()

        return Response(
            {
                "success": True,
                "message": "Payment verified and stock updated",
                "order_id": order.id,
            },
            status=status.HTTP_200_OK,
        )

