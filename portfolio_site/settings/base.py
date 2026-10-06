"""
Base settings for portfolio_site project.
These settings are shared across all environments (development, staging, production).
"""

from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR points to repository root (containing manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Initialize environment variables handler
env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, "insecure-default-change-me"),
    ALLOWED_HOSTS=(list, ["127.0.0.1", "localhost"]),
    DATABASE_URL=(str, f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
    EMAIL_BACKEND=(str, "django.core.mail.backends.console.EmailBackend"),
    EMAIL_HOST=(str, "localhost"),
    EMAIL_PORT=(int, 25),
    EMAIL_USE_TLS=(bool, False),
    EMAIL_HOST_USER=(str, ""),
    EMAIL_HOST_PASSWORD=(str, ""),
    DEFAULT_FROM_EMAIL=(str, "portfolio@example.com"),
    CONTACT_NOTIFICATION_EMAIL=(str, ""),
)

# Read .env file if it exists
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(env_file)

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

# Application definition
INSTALLED_APPS = [
    # Core Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",

    # Project apps
    "core.apps.CoreConfig",
    "projects.apps.ProjectsConfig",
    "notes.apps.NotesConfig",
    "contact.apps.ContactConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # High-performance static asset server
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "portfolio_site.urls"

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
                "django.template.context_processors.media",
                "core.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "portfolio_site.wsgi.application"
ASGI_APPLICATION = "portfolio_site.asgi.application"

# Database Configuration (PostgreSQL in production, SQLite in development)
# Supports DATABASE_URL (Railway, Supabase, Neon, Render) or discrete POSTGRES_* / DB_* env variables
database_url = env("DATABASE_URL", default=None)
if not database_url:
    postgres_db = env("POSTGRES_DB", default=env("DB_NAME", default=None))
    if postgres_db:
        import urllib.parse
        postgres_user = env("POSTGRES_USER", default=env("DB_USER", default="postgres"))
        postgres_password = env("POSTGRES_PASSWORD", default=env("DB_PASSWORD", default=""))
        postgres_host = env("POSTGRES_HOST", default=env("DB_HOST", default="localhost"))
        postgres_port = env("POSTGRES_PORT", default=env("DB_PORT", default="5432"))
        encoded_user = urllib.parse.quote_plus(postgres_user)
        encoded_password = urllib.parse.quote_plus(postgres_password)
        encoded_db = urllib.parse.quote(postgres_db)
        database_url = f"postgres://{encoded_user}:{encoded_password}@{postgres_host}:{postgres_port}/{encoded_db}"

if not database_url:
    database_url = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"

default_db_config = env.db_url_config(database_url)

# Database Connection pooling & Cloud PostgreSQL tuning (Supabase, Railway, Neon, AWS RDS)
is_postgres = default_db_config.get("ENGINE", "").endswith("postgresql")
db_host = str(default_db_config.get("HOST", "")).lower()
db_port = str(default_db_config.get("PORT", ""))
is_supabase = "supabase" in db_host
is_pooler = db_port == "6543" or "pooler" in db_host

# For transaction poolers (such as Supabase PgBouncer port 6543), CONN_MAX_AGE must be 0
if is_pooler:
    default_conn_max_age = 0
elif is_postgres:
    default_conn_max_age = 600
else:
    default_conn_max_age = 0

default_db_config["CONN_MAX_AGE"] = env.int("DB_CONN_MAX_AGE", default=default_conn_max_age)

if is_postgres:
    if "OPTIONS" not in default_db_config:
        default_db_config["OPTIONS"] = {}

    # Supabase and managed databases require SSL
    ssl_required = env.bool("DB_SSL_REQUIRE", default=is_supabase)
    if ssl_required:
        default_db_config["OPTIONS"].setdefault("sslmode", "require")

    # Supabase Transaction Pooler (port 6543) does not support prepared statements
    disable_prepared = env.bool("DB_DISABLE_PREPARED_STATEMENTS", default=is_pooler)
    if disable_prepared:
        default_db_config["OPTIONS"].setdefault("prepare_threshold", 0)

DATABASES = {
    "default": default_db_config
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Rome"  # Italy timezone matching student residence
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Media files (User & Admin uploads)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Email Configuration
EMAIL_BACKEND = env("EMAIL_BACKEND")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
CONTACT_NOTIFICATION_EMAIL = env("CONTACT_NOTIFICATION_EMAIL", default=DEFAULT_FROM_EMAIL)

# Security defaults
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
