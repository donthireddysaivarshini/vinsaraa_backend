from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from decimal import Decimal

from .models import Product, Category, Coupon, SiteConfig
from .serializers import (
    ProductSerializer, 
    CategorySerializer, 
    CouponSerializer, 
    SiteConfigSerializer
)

class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).order_by('-created_at')
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by new arrivals
        is_new = self.request.query_params.get('is_new', None)
        if is_new == 'true':
            queryset = queryset.filter(is_new=True)
        
        return queryset

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

# NEW: Coupon Validation View
class ValidateCouponView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        code = request.data.get('code', '').strip().upper()
        order_total = Decimal(request.data.get('order_total', 0))
        
        if not code:
            return Response({'error': 'Coupon code is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            coupon = Coupon.objects.get(code=code, active=True)
        except Coupon.DoesNotExist:
            return Response({'error': 'Invalid coupon code'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check validity dates
        now = timezone.now()
        if coupon.valid_from > now or coupon.valid_to < now:
            return Response({'error': 'Coupon has expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check minimum order value
        if order_total < coupon.min_order_value:
            return Response({
                'error': f'Minimum order value of ₹{coupon.min_order_value} required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check usage limit
        if coupon.uses_count >= coupon.usage_limit:
            return Response({'error': 'Coupon usage limit exceeded'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate discount
        discount = 0
        if coupon.discount_type == 'percentage':
            discount = (order_total * coupon.value) / 100
        else:  # fixed
            discount = coupon.value
        
        return Response({
            'success': True,
            'discount': float(discount),
            'discount_type': coupon.discount_type,
            'coupon_value': float(coupon.value),
            'message': f'Coupon applied successfully! You saved ₹{discount}'
        }, status=status.HTTP_200_OK)

# NEW: Get Site Configuration
class SiteConfigView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        config = SiteConfig.objects.first()
        if not config:
            # Create default config if none exists
            config = SiteConfig.objects.create()
        
        serializer = SiteConfigSerializer(config)
        return Response(serializer.data, status=status.HTTP_200_OK)