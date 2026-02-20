import os
from pathlib import Path

from metadata_service.schemas import METADATA_COLLECTION


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-key")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "rest_framework",
    "metadata_service",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = []
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "local.sqlite3",
    }
}

REST_FRAMEWORK = {
    "UNAUTHENTICATED_USER": None,
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [],
}

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "metadata_inventory")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", METADATA_COLLECTION)

HTTP_TIMEOUT_SECONDS = float(os.getenv("HTTP_TIMEOUT_SECONDS", "10"))
HTTP_MAX_BODY_BYTES = int(os.getenv("HTTP_MAX_BODY_BYTES", "1000000"))
BACKGROUND_WORKERS = int(os.getenv("BACKGROUND_WORKERS", "4"))
MONGO_CONNECT_RETRIES = int(os.getenv("MONGO_CONNECT_RETRIES", "10"))
MONGO_CONNECT_RETRY_DELAY_SECONDS = float(
    os.getenv("MONGO_CONNECT_RETRY_DELAY_SECONDS", "1.5")
)

STATIC_URL = "/static/"
TIME_ZONE = "UTC"
USE_TZ = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
