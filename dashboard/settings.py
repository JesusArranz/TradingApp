from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-+)73&xuvn+1mfzxg5ayvqky@ha6cc0d#ju-441@t4(r57@*7x0'
DEBUG = False
ALLOWED_HOSTS = ['*']
LOGIN_URL = '/page-login/'





# ------------------------------------------------
# APLICACIONES
# ------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Tu app
    'tradingapp',

    # Allauth para login social
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

SITE_ID = 1

# ------------------------------------------------
# AUTENTICACIÓN
# ------------------------------------------------
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_REDIRECT_URL = '/index-2/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/page-login/'

# ------------------------------------------------
# CONFIGURACIÓN DE GOOGLE (CAMBIA ESTOS DATOS)
# ------------------------------------------------
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': '403703946626-b6qn1s312irf8hf99vtq3jflo00d188n.apps.googleusercontent.com',
            'secret': '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',
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}



# ------------------------------------------------
# MIDDLEWARE
# ------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'tradingapp.utils.RestrictAccessMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# ------------------------------------------------
# TEMPLATES
# ------------------------------------------------
ROOT_URLCONF = 'dashboard.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [Path(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # ← Requerido por allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'custom_context_processor.dz_static',
                'tradingapp.context_processors.global_wallet_balance',
            ],
        },
    },
]

WSGI_APPLICATION = 'dashboard.wsgi.application'

# ------------------------------------------------
# BASE DE DATOS
# ------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ------------------------------------------------
# VALIDACIÓN DE CONTRASEÑAS
# ------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ------------------------------------------------
# CONFIGURACIÓN REGIONAL
# ------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ------------------------------------------------
# ARCHIVOS ESTÁTICOS
# ------------------------------------------------
STATIC_URL = 'static/'
if DEBUG:
    STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# ------------------------------------------------
# CLAVE PRIMARIA POR DEFECTO
# ------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ------------------------------------------------
# CONFIGURACIÓN PARA EVITAR PANTALLA INTERMEDIA DE ALLAUTH
# ------------------------------------------------
SOCIALACCOUNT_AUTO_SIGNUP = True
ACCOUNT_ADAPTER = 'allauth.account.adapter.DefaultAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'tradingapp.adapters.MySocialAccountAdapter'
SOCIALACCOUNT_LOGIN_ON_GET = True
