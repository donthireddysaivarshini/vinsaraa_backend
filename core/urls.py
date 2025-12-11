from django.contrib import admin
from django.urls import path, include # Make sure 'include' is imported
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth APIs
    path('api/auth/', include('accounts.urls')), 
    # Store APIs (NEW)
    path('api/store/', include('store.urls')),
    # Orders & Cart APIs (NEW)
    path('api/orders/', include('orders.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)