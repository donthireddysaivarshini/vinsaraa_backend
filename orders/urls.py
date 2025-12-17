from django.urls import path

from .views import (
    CartView,
    AddToCartView,
    RemoveCartItemView,
    CheckoutView,
    OrderHistoryView,
)

urlpatterns = [
    path("cart/", CartView.as_view(), name="my_cart"),
    path("cart/add/", AddToCartView.as_view(), name="add_to_cart"),
    path("cart/remove/<int:pk>/", RemoveCartItemView.as_view(), name="remove_cart_item"),
    # Checkout
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    # Order history for logged-in user
    path("history/", OrderHistoryView.as_view(), name="order_history"),
]