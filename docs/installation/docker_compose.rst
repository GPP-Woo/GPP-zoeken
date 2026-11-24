.. _installation_docker_compose:

Install using Docker Compose
============================

This installation is meant for people who want to just try out GPP-zoeken on
their own machine.

A `Docker Compose`_ file is available to get the app up and running in minutes.
It contains 'convenience' settings, which means that no additional
configuration is needed to run the app. Therefore, it should **not** be used
for anything other than testing. For example, it includes:

* A default ``SECRET_KEY`` environment variable
* A predefined database with the environment variable
  ``POSTGRES_HOST_AUTH_METHOD=trust``. This lets us connect to the database
  without using a password.
* Debug mode is enabled.
* Admin superuser credentials (``admin`` / ``admin``).
* An API key ``insecure-ea1a8d297e3b2d3313b8a30b18959c3``.

.. _`WSL`: https://docs.microsoft.com/en-us/windows/wsl/

Prerequisites
-------------

You will only need Docker tooling and nothing more:

* `Docker Engine`_ (Desktop or Server)
* `Docker Compose`_ (sometimes comes bundled with Docker Engine)

.. _`Docker Engine`: https://docs.docker.com/engine/install/
.. _`Docker Compose`: https://docs.docker.com/compose/install/


Getting started
---------------

1. Download the project as ZIP-file:

   .. code:: bash

      wget https://github.com/GPP-Woo/GPP-zoeken/archive/refs/heads/main.zip
      unzip main.zip
      cd GPP-zoeken-main

2. Start the docker containers with ``docker compose``. If you want to run the
   containers in the background, add the ``-d`` option to the command below:

   .. code:: bash

      docker compose up


   Docker creates the network, the volumes and the containers of the stack
   (PostgreSQL, Redis, Elastic Search, the web application, a Celery worker and Celery
   Flower) and then shows their logs. The first start takes a while, because the images
   are downloaded and the search index is initialized.

3. Navigate to ``http://127.0.0.1:8000/admin/``, where you can log in with the
   ``admin`` username and ``admin`` password.

4. You can authenticate to the API endpoints with the
   ``Authorization: Token insecure-ea1a8d297e3b2d3313b8a30b18959c3`` HTTP request header.

5. To stop the containers, press *CTRL-C* or if you used the ``-d`` option:

   .. code:: bash

      docker compose stop

6. If you want to get newer versions, you need to ``pull`` because the
   ``docker-compose.yml`` contains no explicit versions:

   .. code:: bash

      docker compose pull
