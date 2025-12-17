from django.urls import path
from .views import CartView, AddToCartView, RemoveCartItemView, CheckoutView # Import CheckoutView

urlpatterns = [
    path('cart/', CartView.as_view(), name='my_cart'),
    path('cart/add/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/remove/<int:pk>/', RemoveCartItemView.as_view(), name='remove_cart_item'),
    
    # New Checkout URL
    path('checkout/', CheckoutView.as_view(), name='checkout'),
]