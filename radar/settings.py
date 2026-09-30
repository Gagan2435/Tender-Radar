import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

env_file = BASE_DIR / ".env"
if env_file.exists():
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            if v.strip():
                os.environ.setdefault(k.strip(), v.strip().strip("\"'"))

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-key-change-me")
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "tenders",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]
ROOT_URLCONF = "radar.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "radar.wsgi.application"

if os.getenv("PGDATABASE"):  # PostgreSQL when configured, SQLite otherwise
    DATABASES = {"default": {
        "ENGINE": "django.db.backends.postgresql", "NAME": os.environ["PGDATABASE"],
        "USER": os.getenv("PGUSER", "postgres"), "PASSWORD": os.getenv("PGPASSWORD", ""),
        "HOST": os.getenv("PGHOST", "localhost"), "PORT": os.getenv("PGPORT", "5432"),
    }}
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

TIME_ZONE = "Asia/Kolkata"
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
