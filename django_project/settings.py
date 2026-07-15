from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-8&_8a1%n!2c6tbw7t#g5@k4v2k9d8j5h2m3w9x7q4z8p6r1n3b'

DEBUG = False

ALLOWED_HOSTS = [
    'web-production-a9ad2f.up.railway.app',
    'localhost',
    '127.0.0.1',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',                    # ← Django REST Framework
    'rest_framework_simplejwt',          # ← Simple JWT (para autenticação)
    'whitenoise.runserver_nostatic',
    'core',
]

# Configuração do REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # <-- ADICIONAR ESTA
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuração do Simple JWT
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

ROOT_URLCONF = 'django_project.urls'

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
                'core.context_processors.moedas_context',  # <-- DEVE ESTAR AQUI
            ],
        },
    },
]

WSGI_APPLICATION = 'django_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-pt'
TIME_ZONE = 'Africa/Maputo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'core/static'),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CSRF_TRUSTED_ORIGINS = [
    'https://web-production-a9ad2f.up.railway.app',
    'https://*.railway.app',
]

LOGIN_URL = 'login'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# ============================================
# CONFIGURAÇÃO DE EMAIL (SMTP)
# ============================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Para Gmail
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'teuemail@gmail.com'  # Substitui pelo teu email
EMAIL_HOST_PASSWORD = 'tuapassword'  # Substitui pela tua password
DEFAULT_FROM_EMAIL = 'Nhonga <noreply@nhonga.com>'

# ============================================
# CONFIGURAÇÕES M-PESA
# ============================================

MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY', '')
MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET', '')
MPESA_PASSKEY = os.environ.get('MPESA_PASSKEY', '')
MPESA_SHORTCODE = os.environ.get('MPESA_SHORTCODE', '174379')  # Código de teste
MPESA_CALLBACK_URL = os.environ.get('MPESA_CALLBACK_URL', 'https://web-production-a9ad2f.up.railway.app/api/mpesa/callback/')
MPESA_ENVIRONMENT = os.environ.get('MPESA_ENVIRONMENT', 'sandbox')  # 'sandbox' ou 'production'

# ============================================
# SEGURANÇA - SESSÕES E CSRF
# ============================================

# Sessões Seguras
SESSION_COOKIE_SECURE = False  # Temporariamente False para resolver o loop
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# CSRF
CSRF_COOKIE_SECURE = False  # Temporariamente False para resolver o loop
CSRF_COOKIE_HTTPONLY = True

# Headers de Segurança
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS - Desativar temporariamente
SECURE_SSL_REDIRECT = False  # <-- MUDAR PARA False
SECURE_HSTS_SECONDS = 0  # <-- MUDAR PARA 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# ============================================
# CONFIGURAÇÕES AWS (MODERAÇÃO DE IMAGENS)
# ============================================

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# ============================================
# CONFIGURAÇÕES DA API REST
# ============================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# CORS (para permitir que a app mobile aceda à API)
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',      # React Native
    'http://localhost:8081',      # React Native Metro
    'http://localhost:8100',      # Ionic
    'http://localhost:4200',      # Angular
    'exp://192.168.1.*:19000',    # Expo
]

CORS_ALLOW_CREDENTIALS = True

# JWT
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# ============================================
# CONFIGURAÇÕES STRIPE (VISA/MASTERCARD)
# ============================================

STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_...')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_...')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_...')
STRIPE_SUCCESS_URL = os.environ.get('STRIPE_SUCCESS_URL', 'https://web-production-a9ad2f.up.railway.app/pagamento/sucesso/')
STRIPE_CANCEL_URL = os.environ.get('STRIPE_CANCEL_URL', 'https://web-production-a9ad2f.up.railway.app/pagamento/cancelado/')

# ============================================
# CONFIGURAÇÕES E-MOLA
# ============================================

EMOLA_API_URL = os.environ.get('EMOLA_API_URL', 'https://e2payments.explicador.co.mz')
EMOLA_CLIENT_ID = os.environ.get('EMOLA_CLIENT_ID', 'test_client')
EMOLA_CLIENT_SECRET = os.environ.get('EMOLA_CLIENT_SECRET', 'test_secret')
EMOLA_WALLET_ID = os.environ.get('EMOLA_WALLET_ID', 'test_wallet')

# ============================================
# CONFIGURAÇÕES DE REDIRECIONAMENTO
# ============================================

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'

