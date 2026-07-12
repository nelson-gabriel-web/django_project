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
    'whitenoise.runserver_nostatic',
    'core',
]

MIDDLEWARE = [
     'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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
# CONFIGURAÇÕES DE REDIRECIONAMENTO
# ============================================

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'

