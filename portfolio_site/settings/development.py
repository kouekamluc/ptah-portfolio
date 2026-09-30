"""
Development settings for portfolio_site project.
"""

from .base import *

DEBUG = True

# In development, use simple static storage to prevent manifest issues before collectstatic
STORAGES["staticfiles"] = {
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Allow all local hosts in development
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "*"]
