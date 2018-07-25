"""
For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import base64       # for ENV_VAR decoding
import json         # for JSON parsing
import os           # for ENV_VARs and path

# General

# Set environment

ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')

# Main secret key use a base64 encoding to avoid possible problems with special
# characters

SECRET_KEY = base64.b64decode(
    os.environ.get('SECRET_KEY')
)

# Admin API token used for quering admin level

API_ADMIN_TOKEN = os.environ.get('API_ADMIN_TOKEN')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

# ------------------------------------------------------------------------------

# Application definition
#
# A list of strings designating all applications that are enabled in this
# Django installation.
#
# See: https://docs.djangoproject.com/en/1.11/ref/settings/#installed-apps

INSTALLED_APPS = [
    # Default Django apps:
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',     # Needed by Allauth
    'django.contrib.staticfiles',

    # Third party apps:
    'allauth',          # For user registration, either via email or social
    'allauth.account',  # For user registration, either via email or social
    'constance',        # Dynamic Django settings.
    'crispy_forms',     # The best way to have Django DRY forms
    'django_countries',     # Provides country choices for use with forms
    'captcha',          # Django reCAPTCHA form field/widget integration app.
    'reversion',        # Provides version control for model instances
    'widget_tweaks',    # Tweak the form field rendering in templates

    # Apps specific for console:
    'botstore',         # Bot store
    'studio',           # Bot studio
    'users',            # All user stuff


]

# The ID, as an integer, of the current site in the django_site database table.

SITE_ID = 1

# ------------------------------------------------------------------------------
#
# Middleware configuration
#
# A list of middleware to use.
#
# See: https://docs.djangoproject.com/en/1.11/ref/settings/#middleware

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',

    # WhiteNoise will now serve your static files
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ------------------------------------------------------------------------------
#
# Authentication configuration
#
# All settings played to user authentication and authorization

AUTHENTICATION_BACKENDS = [

    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Apart of standard Django Hasher we use a custom wrapper to migrate old users
# passwords. After first login users password is updated to standard Django
# PBKDF2 SHA256.
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'users.hashers.PBKDF2WrappedSHA256PasswordHasher',
]

# Legacy constant Salt
LEGACY_SALT = base64.b64decode(
    os.environ.get('LEGACY_SALT')
).decode('utf-8')

LOGIN_REDIRECT_URL = '/home/'

# Allow loging using emails only (kind of industrial standard)
ACCOUNT_AUTHENTICATION_METHOD = 'email'

# Determines whether or not an e-mail address is automatically confirmed by a
# GET request. GET is not designed to modify the server state, though it is
# commonly used for email confirmation. To avoid requiring user interaction,
# consider using POST via Javascript in your email confirmation template as an
# alternative to setting this to True.
ACCOUNT_CONFIRM_EMAIL_ON_GET = True

# The user is required to hand over an e-mail address when signing up.
ACCOUNT_EMAIL_REQUIRED = True

# User is blocked from logging in until the email address is verified.
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

# Default way how User should be showed, we use full name rather than username
ACCOUNT_USER_DISPLAY = lambda user: user.get_full_name()  # noqa: E731, need to be a callable

ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 16
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True

# Retyping passwords is annoying!
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False

# Overide Allauth forms
ACCOUNT_FORMS = {
    'signup': 'users.forms.SignupForm',
    'reset_password': 'users.forms.ResetPasswordForm'
}

# Usernames are setup by application, longer are always harder to guess
ACCOUNT_USERNAME_MIN_LENGTH = 8

# WHITELISTED_EMAIL_DOMAINS (default=[])
# If set restricts registration to emails from the given domains, otherwise do
# nothing. Should be a JSON encoded list: `["example.com", "hutoma.com", "hutoma.ai"]`
WHITELISTED_EMAIL_DOMAINS = json.loads(os.environ.get('WHITELISTED_EMAIL_DOMAINS', '[]'))

# ------------------------------------------------------------------------------
#
# Email
#

#  Let's not use prefixes
EMAIL_SUBJECT_PREFIX = ''
ACCOUNT_EMAIL_SUBJECT_PREFIX = ''

DEFAULT_FROM_EMAIL = 'Hutoma AI <hello@hutoma.ai>'

# Default redirect after user is loged in
LOGIN_REDIRECT_URL = '/'

# ReCaptcha
RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')

NOCAPTCHA = True

# ------------------------------------------------------------------------------
#
# Sessions
#
# Settings for `django.contrib.sessions  sessions are stored in Redis
#
# https://docs.djangoproject.com/en/1.11/ref/settings/#sessions
# http://niwinz.github.io/django-redis/latest/#_configure_as_session_backend

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# We’re using cache-based session storage, this selects the cache to use.
SESSION_CACHE_ALIAS = 'sessions'

# ------------------------------------------------------------------------------
#
# Routing configuration
#
# A string representing the full Python import path to your root URLconf
#
# See: https://docs.djangoproject.com/en/1.11/ref/settings/#root-urlconf

ROOT_URLCONF = 'app.urls'

# ------------------------------------------------------------------------------
#
# Templates
#
# A list containing the settings for all template engines to be used
# with Django.
#
# See: https://docs.djangoproject.com/en/1.11/ref/settings/#templates

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'botstore', 'templates'),
            os.path.join(BASE_DIR, 'studio', 'templates'),
            os.path.join(BASE_DIR, 'users', 'templates'),
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.static',
                'django.template.context_processors.media',
                'django.contrib.messages.context_processors.messages',
                'constance.context_processors.config',
                'app.context_processors.tag_manager',
            ],
        },
    },
]

# ------------------------------------------------------------------------------
#
# Form template
#
# Twitter Bootstrap version 3.
#
# See: http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs

CRISPY_TEMPLATE_PACK = 'bootstrap4'

TOKENFIELD_DELIMITER = '\x9D'


# ------------------------------------------------------------------------------
#
# Tag manager
#
# Configure Google tag manager, GTM is disabled if ID is empty

TAG_MANAGER_ENVIRONMENT = base64.b64decode(
    os.environ.get('TAG_MANAGER_ENVIRONMENT', '')
).decode('utf-8')
TAG_MANAGER_ID = os.environ.get('TAG_MANAGER_ID', '')


# ------------------------------------------------------------------------------
#
# WebServer configuration
#
# The full Python path of the WSGI application object that Django’s built-in
# servers (e.g. runserver) will use.
#
# See: https://docs.djangoproject.com/en/1.11/ref/settings/#wsgi-application

WSGI_APPLICATION = 'app.wsgi.application'

# ------------------------------------------------------------------------------
#
# Database
#
# A dictionary containing the settings for all databases to be used
# with Django.
#
# See: https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DATABASE_NAME', 'console_db'),
        'USER': os.environ.get('DATABASE_USER', 'console_app'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', '12345678'),
        'HOST': os.environ.get('DATABASE_HOST', 'mysql'),
        'PORT': os.environ.get('DATABASE_PORT', '3306'),
        'ATOMIC_REQUESTS': True,
    }
}

# ------------------------------------------------------------------------------
#
# Cache configuration
#
# A dictionary containing the settings for all caches to be used with Django.
#
# https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-CACHES
# http://niwinz.github.io/django-redis/latest/#_configure_as_cache_backend

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': [
            'redis://:{password}@{host}:{port}/1'.format(
                password=os.getenv('CACHE_SERVICE_PASSWORD'),
                host=os.getenv('CACHE_SERVICE_HOST', 'redis'),
                port=os.getenv('CACHE_SERVICE_PORT', 6379)
            ),
        ],
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    },
    'sessions': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': [
            'redis://:{password}@{host}:{port}/2'.format(
                password=os.getenv('CACHE_SERVICE_PASSWORD'),
                host=os.getenv('CACHE_SERVICE_HOST', 'redis'),
                port=os.getenv('CACHE_SERVICE_PORT', 6379)
            ),
        ],
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    }
}


# Don't cache templates for development
TEMPLATES_CACHE_AGE = 0

# ------------------------------------------------------------------------------
#
# Internationalization
#
# https://docs.djangoproject.com/en/1.11/topics/i18n/

# Default language code
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Where to search for translation strings
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'botstore', 'locale'),
    os.path.join(BASE_DIR, 'studio', 'locale'),
    os.path.join(BASE_DIR, 'users', 'locale'),
    os.path.join(BASE_DIR, 'locale'),
]

# Languages we are using
LANGUAGES = [
    ('en', 'English'),
    ('fr', 'Français'),
    ('pl', 'Polski'),
]

# ------------------------------------------------------------------------------
#
# Static files (CSS, JavaScript, Images)
#
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATIC_HOST = os.environ.get('DJANGO_STATIC_HOST', '')

STATIC_URL = STATIC_HOST + '/static/'

# In addition to using a `static/` directory inside your apps, define a list of
# directories where Django will also look for static files that aren’t tied to
# a particular app
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'studio', 'static'),
    os.path.join(BASE_DIR, 'static'),
]

# WhiteNoise comes with a storage back-end which automatically takes care of
# compressing your files and creating unique names for each version so they can
# safely be cached forever.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media
#
# User generated content
MEDIA_URL = os.environ.get('MEDIA_URL')

# ------------------------------------------------------------------------------
#
# API connection
#
# APIs url is different in each environment, timeout error would be thrown
# after 1s
#

API_URL = os.environ.get('API_URL')

# allow five seconds for API calls that make one or more calls to Facebook's API
API_DEFAULT_TIMEOUT = 2
API_FACEBOOK_TIMEOUT = 20

API_CHAT_TIMEOUT = 8

# allow a much longer timeout for async chart loading
API_LOGS_TIMEOUT = 20

# Enables logging of API payloads coming from the API, disabled by default,
# should be used extremely careful as it can potentially log sensitive data
API_RESPONSE_BODY_LOGS = os.environ.get('API_RESPONSE_BODY_LOGS', False)

# Limit size of uploaded files, default 2 megabytes is reflecting natural
# limits of Tomcat
MAX_UPLOAD_SIZE = os.getenv('MAX_UPLOAD_SIZE', 2097152)

# ------------------------------------------------------------------------------
#
# Dynamic settings, can be change without deploy. Remember that they are kept in
# Redis so don't use it for enthing crutial.
#

CONSTANCE_REDIS_CONNECTION = {
    'password': os.getenv('CACHE_SERVICE_PASSWORD'),
    'host': os.getenv('CACHE_SERVICE_HOST', 'redis'),
    'port': os.getenv('CACHE_SERVICE_PORT', 6379),
    'db': 0,
}

CONSTANCE_ADDITIONAL_FIELDS = {
    'on/off': ['django.forms.fields.ChoiceField', {
        'widget': 'django.forms.Select',
        'choices': (('on', 'On'), ('off', 'Off'))
    }],
    'timeout': ['django.forms.fields.IntegerField', {
        'widget': 'django.forms.NumberInput',
        'widget_kwargs': {
            'attrs': {
                'max': 60,
                'min': API_DEFAULT_TIMEOUT,
            }
        }
    }],
}

CONSTANCE_CONFIG = {
    'FACEBOOK_INTEGRATION': ('on', 'Enable Facebook Integrations', 'on/off'),
    'FACEBOOK_WARNING': ('', 'Additional warning message for Facebook Integrations'),
    'API_DEFAULT_TIMEOUT': (
        API_DEFAULT_TIMEOUT,
        'Timeouts for most of the API calls, in seconds, max 60s. Please be '
        'careful. Nothing is safe - @davidmg',
        'timeout'
    ),
    'API_CHAT_TIMEOUT': (
        API_CHAT_TIMEOUT,
        'Timeouts for Chat related APIs calls, in seconds, max 60s',
        'timeout'
    ),
    'API_LOGS_TIMEOUT': (
        API_LOGS_TIMEOUT,
        'Timeouts for Logs related APIs calls, in seconds, max 60s',
        'timeout'
    ),
    'API_FACEBOOK_TIMEOUT': (
        API_FACEBOOK_TIMEOUT,
        'Timeouts for Facebook related APIs calls, in seconds, max 60s',
        'timeout'
    ),
}

CONSTANCE_CONFIG_FIELDSETS = {
    'API': ['API_DEFAULT_TIMEOUT', 'API_CHAT_TIMEOUT', 'API_LOGS_TIMEOUT'],
    'Facebook integration': [
        'FACEBOOK_INTEGRATION', 'FACEBOOK_WARNING', 'API_FACEBOOK_TIMEOUT',
    ]
}

EMAIL_BACKEND = 'app.mail.backends.smtp.EmailBackend'

# ------------------------------------------------------------------------------
#
# Environments specific settings

if ENVIRONMENT == 'development':
    """
    Development settings

    - Run using tls server
    - Run in Debug mode
    - Use local MySQL as database
    - Use Mailhog proxy for outgoing emails
    - Add Django Debug Toolbar
    """

    import socket   # used by django-debug-toolbar

    INSTALLED_APPS += [
        "sslserver",        # Provides TLS for local development
    ]

    DEBUG = os.environ.get('DEBUG', True)

    TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

    TEMPLATES[0]['OPTIONS']['context_processors'] += [
        'django.template.context_processors.debug'
    ]

    # Allow all hosts in development mode
    ALLOWED_HOSTS = ['*']

    # --------------------------------------------------------------------------
    #
    # Email
    #

    EMAIL_PORT = 1025
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'mailhog')

    # --------------------------------------------------------------------------
    #
    # Logging
    #
    # Logs would be colored using `coloredlogs`

    LOG_LEVEL = 'INFO'

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'colored': {
                '()': 'coloredlogs.ColoredFormatter',
                'format': '%(name)s.%(funcName)2s - %(message)s %(filename)s:%(lineno)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'colored',
            },
            'elastic': {
                'class': 'hu_logging.HuLogHandler',
                'log_path': '/tmp/hu_log',
                'log_tag': 'django',
                'es_log_index': 'webconsole-v2',
                'elastic_search_url': os.environ.get('LOGGING_ES_URL'),
                'multi_process': True
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'elastic'],
                'level': os.environ.get('DJANGO_LOG_LEVEL', LOG_LEVEL),
            },
            'app': {
                'handlers': ['console', 'elastic'],
                'level': os.environ.get('LOG_LEVEL', LOG_LEVEL),
            },
            'botstore': {
                'handlers': ['console', 'elastic'],
                'level': os.environ.get('LOG_LEVEL', LOG_LEVEL),
            },
            'studio': {
                'handlers': ['console', 'elastic'],
                'level': os.environ.get('LOG_LEVEL', LOG_LEVEL),
            },
            'users': {
                'handlers': ['console', 'elastic'],
                'level': os.environ.get('LOG_LEVEL', LOG_LEVEL),
            },
            'hu_logging': {
                'handlers': ['console', 'elastic'],
                'level': os.environ.get('LOG_LEVEL', LOG_LEVEL),
            }
        },
    }

    # --------------------------------------------------------------------------
    #
    # django-debug-toolbar

    INSTALLED_APPS += [
        'debug_toolbar',
    ]

    MIDDLEWARE = MIDDLEWARE + [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]

    INTERNAL_IPS = [
        '127.0.0.1',
        '0.0.0.0'
    ]

    # Docker in VM hack

    ip = socket.gethostbyname(
        socket.gethostname()
    )

    INTERNAL_IPS += [
        ip[:-1] + '1'
    ]

    # End of hack

elif ENVIRONMENT == 'test':
    """
    Test settings

    - Use SQLite as database
    """

    # Debug
    #
    # Turn debug off so tests run faster, set Log level to Warning

    DEBUG = False
    DJANGO_LOG_LEVEL = 'DEBUG'
    TEMPLATES[0]['OPTIONS']['debug'] = False

    # Statics
    #
    # Use built-in Django storage
    #
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

    # --------------------------------------------------------------------------
    #
    # Databases
    #
    # Use a faster storage system

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'simple_test_db'
        }
    }

    # Mail settings
    #
    # --------------------------------------------------------------------------

    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025

    # In-memory email backend stores messages in django.core.mail.outbox
    # for unit testing purposes
    EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

    # --------------------------------------------------------------------------
    #
    # Testing

    TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'
    TEST_OUTPUT_DIR = './test_output'

    # --------------------------------------------------------------------------
    #
    # Password hashing
    #
    # Use fast password hasher so tests run faster

    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )

    # --------------------------------------------------------------------------
    #
    # Template loaders
    #
    # Keep templates in memory so tests run faster

    TEMPLATES[0]['APP_DIRS'] = False
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

    # ------------------------------------------------------------------------------
    #
    # Cache configuration - use in-memory for testing
    #
    # A dictionary containing the settings for all caches to be used
    # with Django.
    #
    # https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-CACHES
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
        },
        'sessions': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
        }
    }

elif ENVIRONMENT == 'production':

    """
    Production settings

    - Enable stronger password
    - Use SendGrid for mailing
    - Setup secure Allowed hosts
    - Enable Secure session cookie
    """

    #
    # Security
    #

    # A list of strings representing the host/domain names that this Django
    # site can serve. This is a security measure to prevent HTTP Host header
    # attacks, which are possible even under many seemingly-safe web server
    # configurations.

    # localhost
    ALLOWED_HOSTS_JSON = os.environ.get('ALLOWED_HOSTS', '["localhost"]')
    ALLOWED_HOSTS = json.loads(ALLOWED_HOSTS_JSON)

    # Since it’s trivial for a packet sniffer (e.g. Firesheep) to hijack a user’s
    # session if the session cookie is sent unencrypted, there’s really no good
    # excuse to leave this off. It will prevent you from using sessions on insecure
    # requests and that’s a good thing.
    #
    # Whether to use a secure cookie for the session cookie. If this is set to
    # True, the cookie will be marked as “secure,” which means browsers may
    # ensure that the cookie is only sent under an HTTPS connection.
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # A dotted path to the view function to be used when an incoming request is
    # rejected by the CSRF protection.
    CSRF_FAILURE_VIEW = 'app.errors.handler403_csrf'

    # By default, is_secure() is able to determine whether a request is secure
    # by looking at whether the requested URL uses “https://”. This is
    # important for Django’s CSRF protection, and may be used by your own code
    # or third-party apps.
    #
    # We are using a proxy to set a custom HTTP header that tells Django
    # whether the request came in via HTTPS.
    #
    # https://docs.djangoproject.com/en/2.0/ref/settings/#std:setting-SECURE_PROXY_SSL_HEADER
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # X-XSS-Protection sets the configuration for the cross-site scripting
    # filter built into most browsers. While True set header to:
    # X-XSS-Protection: 1; mode=block
    #
    # https://scotthelme.co.uk/hardening-your-http-response-headers/#x-xss-protection
    SECURE_BROWSER_XSS_FILTER = True

    # X-Content-Type-Options stops a browser from trying to MIME-sniff the
    # content type and forces it to stick with the declared content-type.
    # While True set header to:
    # X-Content-Type-Options: nosniff
    #
    # https://scotthelme.co.uk/hardening-your-http-response-headers/#x-content-type-options
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # HTTP Strict Transport Security is an excellent feature to support on your
    # site and strengthens your implementation of TLS by getting the User Agent
    # to enforce the use of HTTPS. 2592000s = 30 days
    #
    # https://scotthelme.co.uk/hsts-the-missing-link-in-tls/
    SECURE_HSTS_SECONDS = 2592000

    # Password validation
    #
    # The list of validators that are used to check the strength of
    # user’s passwords.
    #
    # See: https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]

    # --------------------------------------------------------------------------
    #
    # Logging
    #

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
            'elastic': {
                'class': 'hu_logging.HuLogHandler',
                'log_path': '/tmp/hu_log',
                'log_tag': 'django',
                'es_log_index': 'webconsole-v2',
                'elastic_search_url': os.environ.get('LOGGING_ES_URL'),
                'multi_process': True
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'elastic'],
                'level': os.environ.get('LOG_LEVEL', 'INFO'),
            },
            'botstore': {
                'handlers': ['console', 'elastic'],
                'level': os.environ.get('LOG_LEVEL', 'INFO'),
            },
            'studio': {
                'handlers': ['console', 'elastic'],
                'level': os.environ.get('LOG_LEVEL', 'INFO'),
            },
            'users': {
                'handlers': ['console', 'elastic'],
                'level': os.environ.get('LOG_LEVEL', 'INFO'),
            },
            'hu_logging': {
                'handlers': ['console', 'elastic'],
                'level': os.environ.get('LOG_LEVEL', 'INFO'),
            }
        },
    }

    # --------------------------------------------------------------------------
    #
    # Email
    #

    EMAIL_HOST = 'mail.smtp2go.com'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    EMAIL_PORT = 2525
    EMAIL_USE_TLS = True

    # --------------------------------------------------------------------------
    #
    # Cache
    #

    # Default cache for Templates set to 15 minutes
    TEMPLATES_CACHE_AGE = 60 * 15

    # --------------------------------------------------------------------------
