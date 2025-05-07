#
# Any machine specific settings when using development settings.
#
# ruff: noqa: F403,F405

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "woo_search",
        "USER": "woo_search",
        "PASSWORD": "woo_search",
        # Empty for localhost through domain sockets or '127.0.0.1' for localhost
        # through TCP.
        "HOST": "",
        "PORT": "",  # Set to empty string for default.
    }
}
