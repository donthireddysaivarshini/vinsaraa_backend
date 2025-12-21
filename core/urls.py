from django.contrib import admin
from django.urls import path, include  # Make sure 'include' is imported
from django.conf import settings
from django.conf.urls.static import static
from web_content.views import WebContentViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# This creates /api/content/hero_slides/, /api/content/promos/, etc.
router.register(r'content', WebContentViewSet, basename='content')

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth APIs
    path("api/auth/", include("accounts.urls")),
    # Store APIs
    path("api/store/", include("store.urls")),
    # Orders & Cart APIs
    path("api/orders/", include("orders.urls")),
    # Payments / Razorpay APIs
    path("api/payments/", include("payments.urls")),
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
