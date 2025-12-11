from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()

# --- 1. Standard Auth Views ---

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


# --- 2. THE FINAL GOOGLE FIX ---

class CustomGoogleOAuth2Client(OAuth2Client):
    def __init__(self, *args, **kwargs):
        if "scope_delimiter" in kwargs:
            del kwargs["scope_delimiter"]
        super().__init__(*args, **kwargs)

    # --- DEBUGGING FUNCTION ---
    def get_access_token(self, code):
        try:
            return super().get_access_token(code)
        except Exception as e:
            # THIS WILL PRINT THE REAL ERROR IN YOUR TERMINAL
            print("--------------------------------------------------")
            print("!!! GOOGLE ERROR DETAILS !!!")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Status Code: {e.response.status_code}")
                print(f"Google says: {e.response.text}") # <--- READ THIS
            else:
                print(f"Error: {e}")
            print("--------------------------------------------------")
            raise e
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = CustomGoogleOAuth2Client  # Use our patched client
    
    # Force the callback_url to be 'postmessage'
    # This matches what React's useGoogleLogin hook sends.
    callback_url = "postmessage"

    def get_serializer_context(self):
        """
        Force 'postmessage' into the validator context.
        This fixes the "Define callback_url in view" error.
        """
        context = super().get_serializer_context()
        context["callback_url"] = "postmessage"
        return context