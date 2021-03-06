# -*- coding: utf-8 -*-
# Django settings for note project.
import os

WEB_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOWED_HOSTS = ['10.112.177.228', '127.0.0.1', ]
DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'  # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = '%s/db/tmitter.sqlite' % WEB_PATH  # Or path to database file if using sqlite3.
DATABASE_USER = ''  # Not used with sqlite3.
DATABASE_PASSWORD = ''  # Not used with sqlite3.
DATABASE_HOST = ''  # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''  # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Shanghai'
#TIME_ZONE = 'America/Chicago'

# 网站信息设置
APP_DOMAIN = 'http://127.0.0.1:8004/'
APP_NAME = 'Shejiao'
APP_VERSION = '1.0.0'

# import djcelery
#配置Broker
# BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
# CELERY_BROKER_TRANSPORT = 'redis'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_BACKEND = 'django-db'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_TIMEZONE = 'Asia/Shanghai'
# celery flower --broker=redis://guest:guest@localhost:6379/0

# 全局分页的每页条数
PAGE_SIZE = 4
# 管理后台列表每页条数
ADMIN_PAGE_SIZE = 20

# 网友空间的好友列表个数限制
FRIEND_LIST_MAX = 10

# Feed 相关的设置
FEED_ITEM_MAX = 20


LANGUAGE_CODE = 'zh-hans'
#LANGUAGE_CODE = 'zh-cn'

DEFAULT_CHARSET = "utf-8"


SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

ugettext = lambda s: s
LANGUAGES = (
    ('zh-hans', u'简体中文'),
    ('en', u'English'),
)

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '%s/statics/uploads/' % WEB_PATH

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/statics/uploads/'

# Default user face
DEFAULT_FACE = '/statics/images/face%d.png'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

CACHE_BACKEND = 'locmem:///'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '&a*2eokltx!i@0ohfk=gp(98z^8po#poq2g8r__d2b)-^gvmn0'

# List of callables that know how to import templates from various sources.
AUTHENTICATION_BACKENDS = (
    'social_core.backends.weibo.WeiboOAuth2',
    'social_core.backends.qq.QQOAuth2',
    'social_core.backends.weixin.WeixinOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_URL_NAMESPACE = 'social'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #    'django.middleware.doc.XViewMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)

ROOT_URLCONF = 'shejiao.urls'

##############2016-02-21############################
# STATIC_ROOT = os.path.join(WEB_PATH,'statics')
STATIC_URL = '/statics/'
STATICFILES_DIRS = [os.path.join(WEB_PATH, 'statics')]
########################################

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
                'django.template.context_processors.csrf',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
        'DIRS': [
            # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
            # Always use forward slashes, even on Windows.
            '%s/templates' % WEB_PATH,
            # Don't forget to use absolute paths, not relative paths.
        ],

        # 'LOADERS' : [
        #     'django.template.loaders.filesystem.load_template_source',
        #     'django.template.loaders.app_directories.load_template_source',
        #     #     'django.template.loaders.eggs.load_template_source',
        # ]

    },
]


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'yonghu',
    'utils',
    'pure_pagination',
    'django_celery_results',
    'social_django',
    'tinymce',
    'haystack',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        # 'django.db.backends.',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'shejiao',  # Or path to database file if using sqlite3.
        'USER': 'root',  # Not used with sqlite3.
        'PASSWORD': '123456',  # Not used with sqlite3.
        'HOST': '127.0.0.1',  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',  # Set to empty string for default. Not used with sqlite3.
        # 'OPTIONS':{'init_command':'SET default_storage_engine=INNODB;'},
    }
}


SOCIAL_AUTH_WEIBO_KEY = '2419266061'
SOCIAL_AUTH_WEIBO_SECRET = '7c7c5c820968e699d30a7dd3fc48c775'

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/index'

AUTH_USER_MODEL = "yonghu.Userprofile"

HAYSTACK_CONNECTIONS = {
    'default':{
        'ENGINE':'haystack.backends.whoosh_cn_backend.WhooshEngine',
        'PATH':os.path.join(WEB_PATH, 'whoosh_index'),
    }
}

HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

HAYSTACK_SEARCH_RESULTS_PER_PAGE = 6