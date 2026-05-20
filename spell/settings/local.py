"""Local development settings."""
from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]  # safe locally only

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"