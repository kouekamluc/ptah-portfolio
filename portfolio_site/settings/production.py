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
