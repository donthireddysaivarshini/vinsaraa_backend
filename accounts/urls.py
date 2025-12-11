from django.urls import path
from .views import RegisterView, CustomTokenObtainPairView, UserProfileView,GoogleLogin
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('signup/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/', UserProfileView.as_view(), name='user_profile'),
    # NEW: Google Login
    path('google/', GoogleLogin.as_view(), name='google_login'),
]