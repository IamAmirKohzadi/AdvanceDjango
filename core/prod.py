import os
from .settings import *
from django.core.exceptions import ImproperlyConfigured


DEBUG = False
CORS_ALLOW_ALL_ORIGINS = False
if not SECRET_KEY:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY is required in production.")
ALLOWED_HOSTS = [h for h in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if h]
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS is required in production.")

CSRF_TRUSTED_ORIGINS = [u for u in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if u] # allowed origins for CSRF-protected requests.
CORS_ALLOWED_ORIGINS = [u for u in os.getenv("DJANGO_CORS_ALLOWED_ORIGINS", "").split(",") if u] # allowed frontend origins for cross-origin API calls.

SECURE_SSL_REDIRECT = True # requests over HTTP are redirected to HTTPS.
SESSION_COOKIE_SECURE = True 
CSRF_COOKIE_SECURE = True 
# SESSION_COOKIE_SECURE && CSRF_COOKIE_SECURE:This instructs the browser to only send these cookies over HTTPS connections.
# Note that this will mean that sessions will not work over HTTP, and the CSRF protection will prevent any POST data being accepted over HTTP (which will be fine if you are redirecting all HTTP traffic to HTTPS).

SECURE_HSTS_SECONDS = 31536000 # tell browsers to always use HTTPS
SECURE_HSTS_INCLUDE_SUBDOMAINS = True # tell browsers to always use HTTPS
SECURE_HSTS_PRELOAD = True # tell browsers to always use HTTPS

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https") #  trust proxy header to detect HTTPS correctly.
