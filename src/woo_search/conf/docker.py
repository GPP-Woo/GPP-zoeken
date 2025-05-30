# ruff: noqa: F403,F405
import os

os.environ.setdefault("DB_USER", os.getenv("DATABASE_USER", "postgres"))
os.environ.setdefault("DB_NAME", os.getenv("DATABASE_NAME", "postgres"))
os.environ.setdefault("DB_PASSWORD", os.getenv("DATABASE_PASSWORD", ""))
os.environ.setdefault("DB_HOST", os.getenv("DATABASE_HOST", "db"))
os.environ.setdefault("DB_CONN_MAX_AGE", "60")

os.environ.setdefault("ENVIRONMENT", "docker")
os.environ.setdefault("LOG_STDOUT", "yes")
os.environ.setdefault("CACHE_DEFAULT", "redis:6379/0")
os.environ.setdefault("CACHE_AXES", "redis:6379/0")

os.environ.setdefault("SESSION_COOKIE_SAMESITE", "Lax")

os.environ.setdefault("ELASTICSEARCH_HOST", "http://localhost:9200")
os.environ.setdefault("ELASTICSEARCH_USER", "elastic")
os.environ.setdefault("ELASTICSEARCH_PASSWORD", "insecure-elastic")

# # Strongly suggested to not use this, but explicitly list the allowed hosts. It is
# used to verify if a redirect is safe or not (open redirect vulnerabilities etc.)
# os.environ.setdefault("ALLOWED_HOSTS", "*")

from .production import *  # noqa isort:skip
