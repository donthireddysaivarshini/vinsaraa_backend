from django.urls import path
from .views import (
    ProductListView, 
    ProductDetailView, 
    CategoryListView,
    ValidateCouponView,
    SiteConfigView
)

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('validate-coupon/', ValidateCouponView.as_view(), name='validate_coupon'),
    path('config/', SiteConfigView.as_view(), name='site_config'),
]