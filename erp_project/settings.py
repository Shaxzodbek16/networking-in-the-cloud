import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    "SECRET_KEY", "django-insecure-f_6$_orf58ft=5yf3ghus0qz!fsmngl9_j+=&lq$aumxr=f7_z"
)
DEBUG = os.getenv("DEBUG", False)

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # local apps
    "accounts",
    "inventory",
    "sales",
    "dashboard",
    # third-party apps
    "crispy_forms",
    "crispy_bootstrap5",
    "django.contrib.humanize",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "erp_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "erp_project.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"

STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_ROOT = os.path.join(BASE_DIR, "media/")
MEDIA_URL = "/media/"

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"
CRISPY_ALLOWED_TEMPLATE_PACKS = ["bootstrap5"]
CRISPY_TEMPLATE_PACK = "bootstrap5"

JAZZMIN_SETTINGS = {
    "site_title": "ERP Admin",
    "site_header": "ERP Control Panel",
    "site_brand": "ERP System",
    "site_logo": None,
    "site_logo_html": (
        "<img src=\"{% static 'logo.svg' %}\" "
        'width="50" height="509" alt="ERP Logo">'
    ),
    "site_icon": "favicon.png",
    "welcome_sign": "Welcome to ERP dashboard!",
    "copyright": "© 2025 My Market LLC",
    "theme": "slate",
    "dark_mode_theme": "darkly",
    "show_ui_builder": True,
    "order_with_respect_to": [
        "dashboard",
        "inventory",
        "sales",
        "accounts",
        "auth",
    ],
    "icons": {
        "dashboard": "fas fa-chart-line",
        "inventory": "fas fa-warehouse",
        "sales": "fas fa-shopping-cart",
        "accounts": "fas fa-user-tag",
        "auth": "fas fa-users-cog",
        "inventory.category": "fas fa-tags",
        "inventory.product": "fas fa-box-open",
        "sales.sale": "fas fa-receipt",
        "sales.saleitem": "fas fa-list",
    },
    "language_chooser": True,
}
JAZZMIN_UI_TWEAKS = {
    "brand_colour": "primary",
    "accent": "cyan",
    "navbar_small_text": False,
    "sidebar_width": "250px",
    "footer_fixed": False,
    "button_classes": {
        "primary": "btn btn-sm btn-primary",
        "secondary": "btn btn-sm btn-secondary",
    },
}
