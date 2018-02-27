"""
Django settings for cornerwise project.
"""

import os
# For celery:
from celery.schedules import crontab
from django.utils.log import DEFAULT_LOGGING

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Determine if the app is in production mode by examining the
# environment variable set by Docker:
APP_MODE = os.environ.get("APP_MODE", "development").lower()
IS_PRODUCTION = (APP_MODE == "production")
IS_CELERY = os.environ.get("IS_CELERY") == "1"

REDIS_HOST = "redis://" + os.environ.get("REDIS_HOST", "")

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET", "98yd3te&#$59^w!j(@b!@f8%fv49&p)vu+8)b4e5jcvfx_yeqs")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = not IS_PRODUCTION

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")
CSRF_COOKIE_SECURE = os.environ.get("CSRF_COOKIE_SECURE", "0") == "1"
SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"

# Application definition
INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django_celery_results",
    "django_pgviews",
    "parcel.ParcelConfig",
    "proposal.ProposalConfig",
    "project.ProjectConfig",
    "user.UserAppConfig",
    "task",
    "shared",
)

MIDDLEWARE_CLASSES = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.SessionAuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
)

ROOT_URLCONF = "cornerwise.urls"

def templates_config():
    context_processors = [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]
    if not IS_PRODUCTION:
        context_processors.insert(0, "django.template.context_processors.debug")

    return [{
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": not IS_PRODUCTION,
            "context_processors": context_processors,
        },
    }]

TEMPLATES = templates_config()

WSGI_APPLICATION = "cornerwise.wsgi.application"

#####################
# Database and Cache

POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "")
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "HOST": POSTGRES_HOST,
        "NAME": "postgres",
        "USER": "postgres"
    },
    "migrate": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "HOST": POSTGRES_HOST,
        "NAME": "postgres",
        "USER": "postgres"
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

CACHES = {
    "default": {
        'BACKEND': 'redis_cache.RedisCache',
        "LOCATION": REDIS_HOST
    }
}

LOGGING = DEFAULT_LOGGING

LOGGING["handlers"]["record"] = {
    "level":       "INFO",
    "class":       "logging.handlers.RotatingFileHandler",
    "filename":    "logs/celery_tasks.log",
    "formatter":   "django.server",
    "maxBytes":    1024*1024*10,
    "backupCount": 5
}

LOGGING["loggers"]["proposal.tasks"] = {
    "handlers": ["console", "mail_admins", "record"],
    "level":    "INFO"
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "US/Eastern"

USE_I18N = True

USE_L10N = True

USE_TZ = True

SERVER_DOMAIN = "cornerwise.org"

STATIC_URL = "/static/"
MEDIA_URL = "/media/"

MEDIA_ROOT = "/media/"
STATICFILES_DIRS = ("/static", "/media")

SERVE_STATIC = os.environ.get("DJANGO_SERVE_STATIC", "1") == "1"
SERVE_MEDIA = os.environ.get("DJANGO_SERVE_MEDIA", "1") == "1"

#######################
# Celery configuration
BROKER_URL = REDIS_HOST

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

# Persist task results to the database
CELERY_RESULT_BACKEND = 'django-cache'

CELERYBEAT_SCHEDULE = {
    "scrape-proposals": {
        "task": "proposal.tasks.pull_updates",
        # Run daily at midnight:
        "schedule": crontab(
            minute=0, hour=0)
    },

    "send-notifications": {
        "task": "user.tasks.send_notifications",
        "schedule": crontab(minute=0, hour=1)
    }
}

CELERYD_TASK_SOFT_TIME_LIMIT = 60

###########
# Messages
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {messages.ERROR: "danger"}

###############################
# Cornerwise-specific settings

GEO_BOUNDS = [
    42.371861543730496,
    -71.13338470458984,  # northwest
    42.40393908425197,
    -71.0679817199707
]  # southeast

# The 'fit-width' of image thumbnails:
THUMBNAIL_DIM = (300, 300)

GEOCODER = "arcgis"

# Email address and name for emails:
EMAIL_ADDRESS = "cornerwise@cornerwise.org"
EMAIL_NAME = "Cornerwise"

# Local settings will override this:
SENDGRID_TEMPLATES = {
    "welcome": "2aa283ce-e020-48b1-bc5c-d47ff2bb5014",
    "replace_subscription": "5d3e9ef4-960b-4fb9-906e-75474dca8720",
    "delete_account": "e5e4fccd-be70-4abf-b6cf-86382926a0f6",
    "threshold": "4422c280-ac97-4668-aef0-6c1c9faaf9d1",
}

# If this is set to True, users are only allowed to have one subscription.
LIMIT_SUBSCRIPTIONS = True

# URL to use for generating minimap raster images for emails, etc.
# MINIMAP_SRC = ("https://minimap.azureedge.net/bounds?"
#                "tile-provider=cartodb-light&"
#                "sw-lat={swlat}&sw-lng={swlon}&"
#                "ne-lat={nelat}&ne-lng={nelon}&clip=1")
MINIMAP_SRC = ("https://minimap.azureedge.net/bounds?"
               "tile-provider=cartodb-light&"
               "sw-lat={swlat}&sw-lng={swlon}&"
               "ne-lat={nelat}&ne-lng={nelon}")

AUTHENTICATION_BACKENDS = ["user.auth.TokenBackend",
                           "django.contrib.auth.backends.ModelBackend"]

IMPORTER_SCHEMA = "https://raw.githubusercontent.com/codeforboston/cornerwise/config/docs/scraper-schema.json"

# Load select environment variables into settings:
for envvar in [
        "GOOGLE_API_KEY", "GOOGLE_BROWSER_API_KEY",
        "GOOGLE_STREET_VIEW_SECRET", "GEOCODER", "ARCGIS_CLIENT_ID",
        "ARCGIS_CLIENT_SECRET", "SOCRATA_APP_TOKEN", "SOCRATA_APP_SECRET",
        "SENDGRID_API_KEY", "FOURSQUARE_CLIENT", "FOURSQUARE_SECRET",
        "SENDGRID_PARSE_KEY"
]:
    globals()[envvar] = os.environ.get(envvar, "")

if not IS_PRODUCTION:
    try:
        # Allow user's local settings to shadow shared settings:
        from .local_settings import *
    except ImportError as err:
        print("Could not find local_settings.py -- ", err)
