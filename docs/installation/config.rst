.. _installation_env_config:

===================================
Environment configuration reference
===================================



Available environment variables
===============================


Required
--------

* ``SECRET_KEY``: Secret key that's used for certain cryptographic utilities. .
* ``ALLOWED_HOSTS``: a comma separated (without spaces!) list of domains that serve the installation. Used to protect against Host header attacks. Defaults to: ``(empty string)``.
* ``CACHE_DEFAULT``: redis cache address for the default cache (this **MUST** be set when using Docker). Defaults to: ``localhost:6379/0``.
* ``CACHE_AXES``: redis cache address for the brute force login protection cache (this **MUST** be set when using Docker). Defaults to: ``localhost:6379/0``.
* ``EMAIL_HOST``: hostname for the outgoing e-mail server (this **MUST** be set when using Docker). Defaults to: ``localhost``.


Database
--------

* ``DB_NAME``: name of the PostgreSQL database. Defaults to: ``woo_search``.
* ``DB_USER``: username of the database user. Defaults to: ``woo_search``.
* ``DB_PASSWORD``: password of the database user. Defaults to: ``woo_search``.
* ``DB_HOST``: hostname of the PostgreSQL database. Defaults to ``db`` for the docker environment, otherwise defaults to ``localhost``.
* ``DB_PORT``: port number of the database. Defaults to: ``5432``.


Celery
------

* ``CELERY_RESULT_BACKEND``: the URL of the backend/broker that will be used by Celery to send the notifications. Defaults to: ``redis://localhost:6379/1``.


Elastic APM
-----------

* ``ELASTIC_APM_SERVER_URL``: URL where Elastic APM is hosted. Defaults to: ``None``.
* ``ELASTIC_APM_SERVICE_NAME``: Name of the service for this application in Elastic APM. Defaults to ``woo_search - <environment>``.
* ``ELASTIC_APM_SECRET_TOKEN``: Token used to communicate with Elastic APM. Defaults to: ``default``.
* ``ELASTIC_APM_TRANSACTION_SAMPLE_RATE``: By default, the agent will sample every transaction (e.g. request to your service). To reduce overhead and storage requirements, set the sample rate to a value between 0.0 and 1.0. Defaults to: ``0.1``.


Elastic Search
--------------

* ``ELASTICSEARCH_HOST``: Host where the ES cluster is deployed, e.g. https://es.example.com:9200. Defaults to: ``(empty string)``.
* ``ELASTICSEARCH_USER``: Username for ES authentication. Defaults to: ``(empty string)``.
* ``ELASTICSEARCH_PASSWORD``: Password for ES authentication. Defaults to: ``(empty string)``.
* ``ELASTICSEARCH_TIMEOUT``: HTTP timeout for ES API interactions. Defaults to: ``60``.
* ``ELASTICSEARCH_CA_CERTS``: Path to CA bundle (in PEM) format if self-signed certificates or a private CA are used to connect to the ES cluster. Alternatively, if EXTRA_VERIFY_CERTS is defined, it will be used. Defaults to: ``(empty string)``.
* ``ELASTICSEARCH_REFRESH``: Refresh control for ES index, update, delete and bulk APIs. In production, you should leave this to the default of 'false'. Defaults to: ``False``.
* ``ELASTICSEARCH_INDEXED_CHARS``: Attachment processor number of chars being used for extraction to prevent huge fields.
    - Use `-1` for no limit.
    - default and max `100000`. Defaults to: ``100000``.
* ``ELASTICSEARCH_MAX_INDEX_FILE_SIZE``: The maximum file size (in bytes) that leads to full text indexing of the file content. For files larger than this limit, only the metadata is indexed. Keep in mind that Elastic Search must be configured appropriately to allow sufficiently large HTTP request body sizes. Defaults to: ``74436090.22556391``.


Optional
--------

* ``SITE_ID``: The database ID of the site object. You usually won't have to touch this. Defaults to: ``1``.
* ``DEBUG``: Only set this to ``True`` on a local development environment. Various other security settings are derived from this setting!. Defaults to: ``False``.
* ``USE_X_FORWARDED_HOST``: whether to grab the domain/host from the X-Forwarded-Host header or not. This header is typically set by reverse proxies (such as nginx, traefik, Apache...). Note: this is a header that can be spoofed and you need to ensure you control it before enabling this. Defaults to: ``False``.
* ``IS_HTTPS``: Used to construct absolute URLs and controls a variety of security settings. Defaults to the inverse of ``DEBUG``.
* ``EMAIL_PORT``: port number of the outgoing e-mail server. Note that if you're on Google Cloud, sending e-mail via port 25 is completely blocked and you should use 487 for TLS. Defaults to: ``25``.
* ``EMAIL_HOST_USER``: username to connect to the mail server. Defaults to: ``(empty string)``.
* ``EMAIL_HOST_PASSWORD``: password to connect to the mail server. Defaults to: ``(empty string)``.
* ``EMAIL_USE_TLS``: whether to use TLS or not to connect to the mail server. Should be True if you're changing the ``EMAIL_PORT`` to 487. Defaults to: ``False``.
* ``DEFAULT_FROM_EMAIL``: The default email address from which emails are sent. Defaults to: ``woo_search@example.com``.
* ``LOG_STDOUT``: whether to log to stdout or not. Defaults to: ``False``.
* ``LOG_LEVEL``: control the verbosity of logging output. Available values are ``CRITICAL``, ``ERROR``, ``WARNING``, ``INFO`` and ``DEBUG``. Defaults to: ``WARNING``.
* ``LOG_QUERIES``: enable (query) logging at the database backend level. Note that you must also set ``DEBUG=1``, which should be done very sparingly!. Defaults to: ``False``.
* ``LOG_REQUESTS``: enable logging of the outgoing requests. Defaults to: ``False``.
* ``SESSION_COOKIE_AGE``: For how long, in seconds, the session cookie will be valid. Defaults to: ``1209600``.
* ``SESSION_COOKIE_SAMESITE``: The value of the SameSite flag on the session cookie. This flag prevents the cookie from being sent in cross-site requests thus preventing CSRF attacks and making some methods of stealing session cookie impossible.Currently interferes with OIDC. Keep the value set at Lax if used. Defaults to: ``Lax``.
* ``CSRF_COOKIE_SAMESITE``: The value of the SameSite flag on the CSRF cookie. This flag prevents the cookie from being sent in cross-site requests. Defaults to: ``Strict``.
* ``ENVIRONMENT``: An identifier for the environment, displayed in the admin depending on the settings module used and included in the error monitoring (see ``SENTRY_DSN``). The default is set according to ``DJANGO_SETTINGS_MODULE``.
* ``SUBPATH``:  Defaults to: ``(empty string)``.
* ``RELEASE``: The version number or commit hash of the application (this is also sent to Sentry).
* ``NUM_PROXIES``: the number of reverse proxies in front of the application, as an integer. This is used to determine the actual client IP adres. On Kubernetes with an ingress you typically want to set this to 2. Defaults to: ``1``.
* ``CSRF_TRUSTED_ORIGINS``: A list of trusted origins for unsafe requests (e.g. POST). Defaults to: ``[]``.
* ``NOTIFICATIONS_DISABLED``: indicates whether or not notifications should be sent to the Notificaties API for operations on the API endpoints. Defaults to ``True`` for the ``dev`` environment, otherwise defaults to ``False``.
* ``DISABLE_2FA``: Whether or not two factor authentication should be disabled. Defaults to: ``False``.
* ``LOG_OUTGOING_REQUESTS_EMIT_BODY``: Whether or not outgoing request bodies should be logged. Defaults to: ``True``.
* ``LOG_OUTGOING_REQUESTS_DB_SAVE``: Whether or not outgoing request logs should be saved to the database. Defaults to: ``False``.
* ``LOG_OUTGOING_REQUESTS_DB_SAVE_BODY``: Whether or not outgoing request bodies should be saved to the database. Defaults to: ``True``.
* ``LOG_OUTGOING_REQUESTS_MAX_AGE``: The amount of time after which request logs should be deleted from the database. Defaults to: ``7``.
* ``SENTRY_DSN``: URL of the sentry project to send error reports to. Default empty, i.e. -> no monitoring set up. Highly recommended to configure this.
* ``ENVIRONMENT_LABEL``:  Defaults to: ``development``.
* ``ENVIRONMENT_BACKGROUND_COLOR``:  Defaults to: ``orange``.
* ``ENVIRONMENT_FOREGROUND_COLOR``:  Defaults to: ``black``.
* ``SHOW_ENVIRONMENT``:  Defaults to: ``True``.
* ``CELERY_TASK_HARD_TIME_LIMIT``:  Defaults to: ``300``.
* ``CELERY_TASK_SOFT_TIME_LIMIT``:  Defaults to: ``60``.
* ``EXTRA_VERIFY_CERTS``: Comma-separated list of additional paths containing certificates (in PEM format) to add to the trust store. Useful when working with self-signed certificates or private certificate authorities. This setting is ignored if 'REQUESTS_CA_BUNDLE' is (already) defined. Defaults to: ``(empty string)``.
* ``DISABLE_APM_IN_DEV``:  Defaults to: ``True``.
* ``PROFILE``:  Defaults to: ``False``.




Specifying the environment variables
=====================================

There are two strategies to specify the environment variables:

* provide them in a ``.env`` file
* start the component processes (with uwsgi/gunicorn/celery) in a process
  manager that defines the environment variables

Providing a .env file
---------------------

This is the most simple setup and easiest to debug. The ``.env`` file must be
at the root of the project - i.e. on the same level as the ``src`` directory (
NOT *in* the ``src`` directory).

The syntax is key-value:

.. code::

   SOME_VAR=some_value
   OTHER_VAR="quoted_value"


Provide the envvars via the process manager
-------------------------------------------

If you use a process manager (such as supervisor/systemd), use their techniques
to define the envvars. The component will pick them up out of the box.
