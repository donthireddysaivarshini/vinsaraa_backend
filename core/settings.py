import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from a local .env file (if present)
# This ensures settings like RAZORPAY_KEY_ID / RAZORPAY_KEY_SECRET
# are available even when you don't manually export them in the shell.
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-change-me-later'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    # Jazzmin (Must be before admin)
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third Party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    # GOOGLE AUTH PACKAGES (ADD THESE)
    'rest_framework.authtoken',               # <--- NEW
    'dj_rest_auth',                           # <--- NEW
    'django.contrib.sites',                   # <--- NEW
    'allauth',                                # <--- NEW
    'allauth.account',                        # <--- NEW
    'allauth.socialaccount',                  # <--- NEW
    'allauth.socialaccount.providers.google', # <--- NEW
    'dj_rest_auth.registration',              # <--- NEW
    

    # My Apps
    'accounts',
    'store',
    'orders',
    'payments',
    'web_content',
]
# REQUIRED BY 'django.contrib.sites'
SITE_ID = 1  # <--- NEW (Add this right after INSTALLED_APPS)

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # CORS First
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Add this line specifically for Allauth
    'allauth.account.middleware.AccountMiddleware', # <--- NEW
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database (Default SQLite for now)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Auth User Model (CRITICAL)
AUTH_USER_MODEL = 'accounts.CustomUser'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata' # Set to India time
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (Product Images)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Config
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny', # Change to IsAuthenticated later
    ]
}

# CORS Config (Allow Frontend)
CORS_ALLOW_ALL_ORIGINS = True # Easier for dev, restrict in prod

# JWT Config
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Jazzmin Admin UI Config
JAZZMIN_SETTINGS = {
    "site_title": "Vinsaraa Admin",
    "site_header": "Vinsaraa",
    "site_brand": "Vinsaraa Collections",
    "welcome_sign": "Welcome to Vinsaraa Admin",
    "search_model": "accounts.CustomUser",

    # 🔒 Disable UI builder (IMPORTANT)
    "show_ui_builder": False,

    # 📍 Sidebar always expanded
    "navigation_expanded": True,

    # 🧷 FIX SIDEBAR (THIS IS THE KEY)
    "sidebar_fixed": True,

    # 🧷 FIX NAVBAR (optional but recommended)
    "navbar_fixed": True,

    # 📌 App order stays consistent
    "order_with_respect_to": [
        "store",
        "orders",
        "web_content",
        "accounts",
        "auth",
        "authtoken",
        "sites",
        "socialaccount",
    ],
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',             # Default Django Auth
    'allauth.account.auth_backends.AuthenticationBackend',   # Google Auth
]
# --- GOOGLE AUTH SETTINGS ---
ACCOUNT_EMAIL_VERIFICATION = 'none' 
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
# This ensures we get the user's email and profile from Google
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

# --- Razorpay Credentials (Loaded from Environment) ---
RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET", "")
RAZORPAY_WEBHOOK_SECRET = os.environ.get("RAZORPAY_WEBHOOK_SECRET", "")
# --- JWT SETTINGS FOR SOCIAL LOGIN ---
REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': 'vinsaraa-auth',
    'JWT_AUTH_REFRESH_COOKIE': 'vinsaraa-refresh',
}


# 3. Keep this for backward compatibility
REST_USE_JWT = True