# settings.py — Produção no GCP
from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "chave-padrao-insegura")
DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "34.95.220.242",
    "1bcd75d3982d.ngrok-free.app"
]

CSRF_TRUSTED_ORIGINS = [
    "http://34.95.220.242",
    "https://34.95.220.242",
    "https://1bcd75d3982d.ngrok-free.app"
]

DOMAIN_NAME = os.getenv("DOMAIN_NAME")
if DOMAIN_NAME:
    ALLOWED_HOSTS.append(DOMAIN_NAME)
    CSRF_TRUSTED_ORIGINS.append(f"https://{DOMAIN_NAME}")
    CSRF_TRUSTED_ORIGINS.append(f"http://{DOMAIN_NAME}")

API_KEY_SEFAZ = os.getenv("API_KEY_SEFAZ")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "usuarios",
    "participantes",
    "cupons",
    "skus_validos",
    "promocaobombril",
    "log_sistema",
    "campanha",
    "rest_framework",
    "rest_framework.authtoken",
    "widget_tweaks",
    "django_celery_beat",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "gestor_campanha.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "gestor_campanha.wsgi.application"

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

AUTH_USER_MODEL = "usuarios.Usuarios"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "sistema"
LOGOUT_REDIRECT_URL = "login"

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600

DATE_FORMAT = "d/m/Y"
DATE_INPUT_FORMATS = ["%d/%m/%Y"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# para permitir iframe no html
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Email (SMTP) configuration
# Env variables expected: EMAIL_HOST_SMTP, EMAIL_PORT, EMAIL_USER, EMAIL_SENHA
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST_SMTP', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('EMAIL_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_SENHA', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False') == 'True'
# If SSL is enabled, Django ignores TLS. Ensure only one is true in env.
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'nao-responda@promocaobombril.com.br')
DEFAULT_FROM_NAME = os.getenv('DEFAULT_FROM_NAME', 'Promoção Bombril')

# Brevo (Sendinblue) API configuration for transactional emails
BREVO_API_KEY = os.getenv('BREVO_API_KEY', '')