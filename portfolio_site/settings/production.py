"""
Production settings for portfolio_site project.
Strict security, SSL redirects, and production database enforcement.
"""

from .base import *

DEBUG = False

# Allowed Hosts from environment variable (comma-separated)
ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS", 
    default=["localhost", "127.0.0.1", "0.0.0.0", ".railway.app", ".up.railway.app"]
)

# CSRF Trusted Origins (Mandatory for Railway, Render, and custom domains with HTTPS)
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=[
        "https://*.railway.app",
        "https://*.up.railway.app",
        "https://localhost",
        "https://127.0.0.1",
    ]
)

# Production SSL & Cookie Security
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=True)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=True)
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

# Persistent Media Volume Support (for Railway persistent volume mounts)
RAILWAY_VOLUME_MOUNT_PATH = env("RAILWAY_VOLUME_MOUNT_PATH", default="")
if RAILWAY_VOLUME_MOUNT_PATH:
    MEDIA_ROOT = Path(RAILWAY_VOLUME_MOUNT_PATH) / "media"
    MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

# Database check & SSL enforcement for production
if DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3":
    import logging
    logging.getLogger("django.security").warning(
        "Production environment is currently using SQLite. "
        "For multi-worker concurrency and persistent data across deploys, set DATABASE_URL with PostgreSQL."
    )
elif DATABASES["default"]["ENGINE"].endswith("postgresql"):
    db_host = str(DATABASES["default"].get("HOST", "")).lower()
    is_local_host = db_host in ("localhost", "127.0.0.1", "db", "")
    if not is_local_host and env.bool("DB_SSL_REQUIRE", default=True):
        DATABASES["default"].setdefault("OPTIONS", {}).setdefault("sslmode", "require")

# Production Logging Configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} [{name}:{lineno}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
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
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
