"""
Django settings for cornerwise project.
"""

import os
import re
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


def dev_default(var_name, default=True):
    """If the environment variable `var_name` is set, use it to determine whether a
    feature is turned on. Otherwise, fall back on `default` in development mode
    and `not default` in production mode.

    """
    return os.environ[var_name] == "1" if var_name in os.environ else IS_PRODUCTION != default

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = not IS_PRODUCTION or os.environ.get("DJANGO_DEBUG_MODE") == "1"

SERVE_STATIC = dev_default("DJANGO_SERVE_STATIC")
SERVE_MEDIA = dev_default("DJANGO_SERVE_MEDIA")

ALLOWED_HOSTS_RAW = os.environ.get("ALLOWED_HOSTS", "*")
ALLOWED_HOSTS = ALLOWED_HOSTS_RAW.split(",")

VIRTUAL_HOST = os.environ.get("VIRTUAL_HOST")

CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE = dev_default("SECURE_COOKIES", False)
SESSION_COOKIE_DOMAIN = CSRF_COOKIE_DOMAIN = \
    os.environ.get("COOKIE_DOMAIN") \
    or (VIRTUAL_HOST and VIRTUAL_HOST.split(",")[0]) \
    or (ALLOWED_HOSTS[0] if ALLOWED_HOSTS_RAW != "*" else None)

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
    "django.contrib.postgres",
    "django_celery_results",
    "django_pgviews",
    "tinymce",
    "parcel.ParcelConfig",
    "proposal.ProposalConfig",
    "project.ProjectConfig",
    "user.UserAppConfig",
    "shared.SharedAppConfig",
    "task",
)

MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "site_config.SiteMiddleware",
)

ROOT_URLCONF = "cornerwise.urls"


def templates_config():
    context_processors = [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "site_config.context_processor",
    ]
    if DEBUG:
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
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_HOST,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_CLASS": "redis.BlockingConnectionPool",
            "CONNECTION_POOL_CLASS_KWARGS": {
                "max_connections": 50,
                "timeout": 20
            },
            "TIMEOUT": None
        }
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

LOGGING["loggers"]["celery_tasks"] = {
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

# Files to be copied when static files are collected for deployment.
STATICFILES_DIRS = [
    ("images", "/static/images"),
    ("errors", "/static/errors"),
    ("layerdata", "/static/scripts/src/layerdata"),
    ("css", "/static/css"),
    ("scripts", "/static/scripts"),
]


def get_built_resources():
    with open("/static/build/built.json", "r") as built:
        import json
        info = json.load(built)
        return info["js_filename"], info["css_filename"]


if not SERVE_STATIC:
    STATICFILES_DIRS.extend([
        ("build", "/static/build"),
    ])

    STATIC_ROOT = "/static_build"

    try:
        JS_FILENAME, CSS_FILENAME = get_built_resources()
    except:
        JS_FILENAME = "app.build.js"
        CSS_FILENAME = "app.build.css"
else:
    JS_FILENAME = CSS_FILENAME = ""
    STATICFILES_DIRS.extend([
        ("template", "/static/template"),
    ])

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
    },

    "cleanup-subscriptions": {
        "task": "user.tasks.cleanup_subscriptions",
        "schedule": crontab(minute=0, hour=0)
    },

    "collect-sendgrid-stats": {
        "task": "user.tasks.collect_sendgrid_stats",
        "schedule": crontab(minute=0, hour=2, day_of_week=0)
    },
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
# Set to a color name to pad thumbnails to the desired dimensions
THUMBNAIL_PAD = None

GEOCODER = "arcgis"

# Email address and name for emails:
EMAIL_ADDRESS = "cornerwise@cornerwise.org"
EMAIL_NAME = "Cornerwise"

# TinyMCE configuration:
# TINYMCE_JS_URL = 'http://debug.example.org/tiny_mce/tiny_mce_src.js'
TINYMCE_DEFAULT_CONFIG = {
    "plugins": "paste,searchreplace",
    "theme": "advanced",
    "theme_advanced_buttons2": "",
    "theme_advanced_buttons3": "",
    "theme_advanced_path": False,
    "cleanup_on_startup": True,
    "custom_undo_redo_levels": 10,
}
TINYMCE_SPELLCHECKER = False
TINYMCE_COMPRESSOR = True

# Local settings will override this:
SENDGRID_TEMPLATES = {
    "generic": "5b82e3d6-151a-44e0-82ec-a6fdcae746bb",
}

MIN_ALERT_RADIUS = 50
MAX_ALERT_RADIUS = 10000

# URL to use for generating minimap raster images for emails, etc.
MINIMAP_SRC = ("https://minimap.azureedge.net/bounds?"
               "tile-provider=cartodb-light&"
               "sw-lat={swlat}&sw-lng={swlon}&"
               "ne-lat={nelat}&ne-lng={nelon}&circle={circle}")

GEO_REGION = "Somerville, MA"

AUTHENTICATION_BACKENDS = ["user.auth.TokenBackend",
                           "django.contrib.auth.backends.ModelBackend"]

IMPORTER_SCHEMA = "https://raw.githubusercontent.com/codeforboston/cornerwise/master/docs/scraper-schema.json"

# Site config
SITE_CONFIG = {
    "somerville": {
        "module": "site_config.somervillema",
        "hostnames": ["somerville.cornerwise.org", "cornerwise.somervillema.gov", "default"]
    },
    # "cambridge": {
    #     "module": "site_config.cambridgema",
    #     "hostnames": ["cambridge.cornerwise.org"]
    # }
}

USE_SITE_HOSTNAMES = True

# Load select environment variables into settings:
for envvar in [
        "GOOGLE_API_KEY", "GOOGLE_BROWSER_API_KEY",
        "GOOGLE_STREET_VIEW_SECRET", "GEOCODER", "ARCGIS_CLIENT_ID",
        "ARCGIS_CLIENT_SECRET", "SOCRATA_APP_TOKEN", "SOCRATA_APP_SECRET",
        "SENDGRID_API_KEY", "FOURSQUARE_CLIENT", "FOURSQUARE_SECRET",
        "SENDGRID_PARSE_KEY", "SERVER_DOMAIN", "BASE_URL", "SITE_REDIRECT"
]:
    if envvar in os.environ or envvar not in globals():
        globals()[envvar] = os.environ.get(envvar, "")


# If the user accesses the site via a domain that does not match any of the
# configured domains and SITE_REDIRECT is set to 1, redirect requests to the
# default hostname.
SITE_REDIRECT = SITE_REDIRECT == "1"

def get_admins():
    admins_from_env = []
    for admin_str in re.split(r"\s*;\s*", os.environ.get("ADMINS", "")):
        m = re.search(r"\s*<([^>]+)>", admin_str)
        username, email = \
            (admin_str[0:m.start()], m.group(1).strip()) if m \
            else (admin_str, admin_str)

        admins_from_env.append((username, email))
    return admins_from_env


ADMINS = get_admins()

if IS_PRODUCTION and not ADMINS:
    print("No ADMINS configured.")


if not IS_PRODUCTION:
    try:
        # Allow user's local settings to shadow shared settings:
        from .local_settings import *
    except ImportError as err:
        print("Could not find local_settings.py -- ", err)


if SENDGRID_API_KEY:
    EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
    SENDGRID_SANDBOX_MODE_IN_DEBUG = False
