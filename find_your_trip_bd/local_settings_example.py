from decouple import config
from .settings import *
import os


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT"),
        "ATOMIC_REQUESTS": True,
    }
}


# General
DEBUG = True
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "utils.storages.CustomStaticFilesStorage"

# districts
DISTRICT_DATA_URL = config("DISTRICT_DATA_URL")
WEATHER_API_URL = config("WEATHER_API_URL")
AIR_QUALITY_API_URL = config("AIR_QUALITY_API_URL")
