.. _installation_requirements:

Requirements
============

Elastic Search
--------------

Currently we only support Elastic Search 8.x as search index.

GPP-publicatiebank
------------------

GPP-zoeken receives the publications, documents and topics to index from
`GPP-publicatiebank <https://gpp-publicatiebank.readthedocs.io/>`_ (or an equivalent
alternative). To index the contents of documents, GPP-zoeken downloads them from
GPP-publicatiebank, which requires a :ref:`service <configuration_services>`. See
:ref:`versions` for the supported versions.

Processes
---------

The container image provides scripts to start each process that makes up a complete
GPP-zoeken deployment. All of them use the same image and environment variables.

* ``/start.sh`` - the web application (admin and API).
* ``/celery_worker.sh`` - the background task workers that index the documents in
  Elastic Search. You can run as many replicas as needed.
* ``/celery_flower.sh`` - optional, a web interface to monitor the background tasks.

GPP-zoeken has no periodic tasks, so a Celery beat process is not needed.

Initializing the search index
-----------------------------

On a fresh Elastic Search cluster, the indices must be created and the document mappings
populated before GPP-zoeken can index anything. Run
``python src/manage.py initialize_mappings --wait`` in an init container or a separate
job, or set ``INIT_ES_INDICES=true`` so that ``/start.sh`` runs it before starting the
web application. The command is safe to run multiple times.

With ``--wait``, the command waits until Elastic Search is reachable and reports itself
healthy, by default for at most 60 seconds. ``/start.sh`` reads this timeout (in
seconds) from ``ES_WAIT_TIMEOUT``. If the cluster does not become healthy in time, the
command exits with a non-zero status, so the init container or job fails visibly.

Tuning the processes
--------------------

The start scripts read the following environment variables, in addition to the
:ref:`environment configuration <installation_env_config>`.

**Web application** (``/start.sh``, uWSGI)

* ``UWSGI_PORT``: the port to listen on. Defaults to ``8000``.
* ``UWSGI_PROCESSES``: the number of worker processes. Defaults to ``4``.
* ``UWSGI_THREADS``: the number of threads per process. Defaults to ``1``.
* ``UWSGI_HARAKIRI``: the maximum time in seconds a request may take before the worker
  is recycled. Defaults to ``1800``.
* ``UWSGI_POST_BUFFERING``: the size (in bytes) above which request bodies are buffered
  to disk. Defaults to ``8192``.
* ``UWSGI_BUFFER_SIZE``: the internal buffer size (in bytes) for request headers.
  Defaults to ``65535``.
* ``INIT_ES_INDICES`` and ``ES_WAIT_TIMEOUT``: see
  `Initializing the search index`_ above.

Other ``UWSGI_*`` variables are also picked up by uWSGI.

**Background task workers** (``/celery_worker.sh``)

* ``CELERY_WORKER_CONCURRENCY``: the number of concurrent worker processes. Defaults to
  ``1``.
* ``CELERY_WORKER_QUEUE`` and ``CELERY_WORKER_NAME``: the queue to consume and the name
  of the worker. Default to ``celery`` and ``celery@<hostname>``.
* ``CELERY_LOGLEVEL``: the log level of the workers. Defaults to ``INFO``.
