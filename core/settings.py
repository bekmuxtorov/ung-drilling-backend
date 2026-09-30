import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# .env faylini yuklash
load_dotenv(BASE_DIR / '.env', override=True)

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-drilling-rig-management-secret-key-prod-change-me')

DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')

raw_hosts = os.getenv('ALLOWED_HOSTS', '*')
ALLOWED_HOSTS = [h.strip() for h in raw_hosts.split(',') if h.strip()]
if DEBUG:
    ALLOWED_HOSTS = list(set(ALLOWED_HOSTS + ['*', 'localhost', '127.0.0.1']))

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Uchinchi tomon kutubxonalari
    'rest_framework',
    'django_filters',
    'corsheaders',
    'drf_spectacular',

    # Mahalliy app'lar
    'apps.common',
    'apps.directory',
    'apps.operations',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

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

WSGI_APPLICATION = 'core.wsgi.application'

# PostgreSQL Ma'lumotlar bazasi sozlamalari (.env orqali boshqariladi)
DB_ENGINE = os.getenv('DB_ENGINE', 'django.db.backends.postgresql')

if 'sqlite' in DB_ENGINE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / os.getenv('DB_NAME', 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': os.getenv('DB_NAME', 'ung_drilling_db'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'CONN_MAX_AGE': int(os.getenv('DB_CONN_MAX_AGE', '60')),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'uz-uz'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework sozlamalari
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# ==============================================================================
# OpenAPI 3.0 / Swagger Sozlamalari (drf-spectacular)
# ==============================================================================
SPECTACULAR_SETTINGS = {
    'TITLE': "UNG | Quduqlar qurilishi bo'yicha boshqaruv tizimi API",
    'DESCRIPTION': (
        "## Quduqlar qurilishi bo'yicha boshqaruv tizimi API\n\n"
        "Ushbu API quduqlar qurilishi, VBM (Vishka-montaj) operatsiyalari, bosqichlar (demontaj, tashish, montaj), "
        "kunlik ish hisobotlari, transport vositalari hamda barcha tizim ma'lumotnomalarini boshqarish uchun mo'ljallangan.\n\n"
        "### 📌 Imkoniyatlar va Qulayliklar:\n"
        "- **CRUD operatsiyalari**: Har bir resurs uchun to'liq Create, Read, Update, Delete amallari mavjud.\n"
        "- **Optimallashtirilgan so'rovlar**: N+1 so'rovlar oldi olingan (`select_related`, `prefetch_related`).\n"
        "- **Qidiruv (Search)**: Ro'yxatlar bo'yicha `?search=nomi` parametri orqali tezkor qidiruv.\n"
        "- **Filtrlash (Filter)**: Masalan, maydonlar, sanalar, usta, bajarilish foizi bo'yicha filtrlash.\n"
        "- **Saralash (Ordering)**: `?ordering=field` yoki `?ordering=-field` orqali saralash.\n"
        "- **Paginatsiya**: Har bir so'rovda `page` va `page_size` parametrlarini uzatish imkoniyati (`max_page_size=100`).\n"
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'TAGS': [
        {'name': 'VBM Operatsiyalari (Vishka-montaj)', 'description': 'Burg\'ulash qurilmasini ko\'chirish va montaj qilish operatsiyalari'},
        {'name': 'Operatsiya bosqichlari (Stages)', 'description': 'Demontaj, Tashish va Montaj bosqichlari (reja/fakt kunlar va sanalar)'},
        {'name': 'Kunlik ish hisobotlari (Daily Works)', 'description': 'Har bir operatsiya bo\'yicha kunlik bajarilgan ishlar tavsifi'},
        {'name': 'Kunlik transport vositalari', 'description': 'Kunlik ishlarga jalb qilingan transport vositalari va ularning soni'},
        {'name': 'Korxonalar', 'description': 'Tashkilot va korxonalarni boshqarish endpointlari'},
        {'name': "Burg'ulash uskunalari", 'description': "Burg'ulash uskunasi turlari ma'lumotnomasi"},
        {'name': 'Hududlar (Viloyatlar)', 'description': 'Viloyatlar va hududlar ma\'lumotnomasi'},
        {'name': 'Maydonlar (Konlar)', 'description': 'Neft va gaz konlari / maydonlari boshqaruvi'},
        {'name': 'Ustalar (Foremen)', 'description': "Burg'ulash ustalari va prorablar ro'yxati"},
        {'name': 'Transport turlari', 'description': 'Tashish va operatsiyalar uchun transport vositalari turlari'},
        {'name': 'Lavozimlar', 'description': 'Korxonadagi lavozimlar ma\'lumotnomasi'},
        {'name': 'Xodimlar', 'description': 'Xodimlarni ro\'yxatga olish va lavozimlarga biriktirish'},
        {'name': 'Operatsiya bosqichlari', 'description': 'Demontaj, tashish va montaj operatsiya bosqichlari ro\'yxati (Enum)'},
    ],
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': False,
        'filter': True,
        'docExpansion': 'list',
        'defaultModelsExpandDepth': 2,
        'defaultModelExpandDepth': 2,
    },
}

# CORS sozlamalari
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]
