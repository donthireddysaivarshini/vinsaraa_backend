from django.urls import path
from .views import CartView, AddToCartView, RemoveCartItemView, CheckoutView # Import CheckoutView
from .views import UserOrdersView, order_status, update_order_status
from .views import SavedAddressListCreateView, SavedAddressDetailView
urlpatterns = [
    path('cart/', CartView.as_view(), name='my_cart'),
    path('cart/add/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/remove/<int:pk>/', RemoveCartItemView.as_view(), name='remove_cart_item'),
     path("", UserOrdersView.as_view(), name="user-orders"),          # GET /orders/
    path("<int:pk>/status/", order_status, name="order-status"),     # GET /orders/<id>/status/
    path("<int:pk>/update-status/", update_order_status, name="update-order-status"),  # PATCH /orders/<id>/update-status/
    
    # New Checkout URL
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('addresses/', SavedAddressListCreateView.as_view(), name='saved-addresses'),
    path('addresses/<int:pk>/', SavedAddressDetailView.as_view(), name='saved-address-detail'),
]