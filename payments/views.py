from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging
import razorpay

logger = logging.getLogger(__name__)

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
            order.payment_status = "Pending" #should change to paid"
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


@method_decorator(csrf_exempt, name="dispatch")
class RazorpayWebhookView(APIView):
    """
    Endpoint for Razorpay webhooks. Verifies signature using
    `RAZORPAY_WEBHOOK_SECRET` and processes `payment.captured` events.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        raw_body = request.body
        signature = request.headers.get("X-Razorpay-Signature") or request.META.get(
            "HTTP_X_RAZORPAY_SIGNATURE"
        )

        webhook_secret = getattr(request._request, "RAZORPAY_WEBHOOK_SECRET", None)
        # fallback to settings
        if not webhook_secret:
            from django.conf import settings

            webhook_secret = getattr(settings, "RAZORPAY_WEBHOOK_SECRET", None)

        if not signature or not webhook_secret:
            logger.error("Webhook request missing signature or webhook secret not configured")
            return Response({"error": "Invalid webhook request"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify signature
        try:
            # client utility requires a client instance
            from django.conf import settings as _settings

            try:
                client = razorpay.Client(auth=(
                    getattr(_settings, "RAZORPAY_KEY_ID", ""),
                    getattr(_settings, "RAZORPAY_KEY_SECRET", ""),
                ))
            except Exception:
                client = razorpay.Client()

            client.utility.verify_webhook_signature(raw_body, signature, webhook_secret)
        except Exception as exc:
            logger.exception("Invalid webhook signature: %s", exc)
            return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

        # Process event
        data = request.data
        event = data.get("event")

        if event == "payment.captured":
            try:
                payload = data.get("payload", {})
                payment_entity = payload.get("payment", {}).get("entity", {})
                razorpay_order_id = payment_entity.get("order_id")
                razorpay_payment_id = payment_entity.get("id")

                if not razorpay_order_id or not razorpay_payment_id:
                    logger.error("Webhook payment.captured missing order_id/payment_id")
                    return Response(status=status.HTTP_400_BAD_REQUEST)

                # Idempotent processing: find order and mark paid if not already
                from django.db import transaction
                from orders.models import Order
                from store.models import ProductVariant

                with transaction.atomic():
                    order = (
                        Order.objects.select_for_update()
                        .prefetch_related("items")
                        .filter(razorpay_order_id=razorpay_order_id)
                        .first()
                    )

                    if not order:
                        logger.error("Order not found for razorpay_order_id=%s", razorpay_order_id)
                        return Response(status=status.HTTP_404_NOT_FOUND)

                    if order.payment_status.lower() == "paid":
                        logger.info("Order %s already marked as paid", order.id)
                        return Response({"status": "ok"}, status=status.HTTP_200_OK)

                    # Update order payment fields
                    order.razorpay_payment_id = razorpay_payment_id
                    order.payment_status = "Paid"
                    order.order_status = "paid"

                    # Deduct stock
                    for item in order.items.all():
                        size = None
                        if item.variant_label and ":" in item.variant_label:
                            size = item.variant_label.split(":", 1)[1].strip()

                        if not size:
                            raise ValueError("Invalid variant label on order item.")

                        variant = (
                            ProductVariant.objects.select_for_update()
                            .filter(product__title=item.product_name, size=size)
                            .first()
                        )

                        if not variant:
                            logger.error("Variant not found for item %s", item.product_name)
                            return Response({"error": "Variant not found"}, status=status.HTTP_400_BAD_REQUEST)

                        if variant.stock < item.quantity:
                            logger.error("Out of stock for item %s", item.product_name)
                            return Response({"error": "Out of stock"}, status=status.HTTP_400_BAD_REQUEST)

                        variant.stock -= item.quantity
                        variant.save()

                    order.save()

                logger.info("Processed webhook and marked order %s as paid", order.id)
                return Response({"status": "ok"}, status=status.HTTP_200_OK)
            except Exception as exc:
                logger.exception("Error processing webhook: %s", exc)
                return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Unhandled event types
        logger.info("Received unhandled webhook event: %s", event)
        return Response({"status": "ignored"}, status=status.HTTP_200_OK)

