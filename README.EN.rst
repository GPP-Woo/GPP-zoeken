==========
GPP-zoeken
==========

:Version: 2.0.0
:Source: https://github.com/GPP-Woo/GPP-zoeken
:Keywords: WOO, Public Documents, NL, Open Data

|docs| |docker|

A search component providing the functionalities for a "public documents" index.

(`Nederlandse versie`_)

Developed by `Maykin B.V.`_ for ICATT and Dimpact.

Introduction
============

In the Netherlands, legislation require governments to act from the principles of
Openness (`Wet Open Overheid (Dutch) <https://www.rijksoverheid.nl/onderwerpen/wet-open-overheid-woo>`_).
Government organizations are required - by law - to actively
publish documents produced for the Public sphere, making them accessible to interested
parties/citizens. Dimpact provides a Generic Publication Platform to facilitate this for
municipalities, of which the Public Documents Registration component is one part.

GPP-zoeken makes it possible to index and search published documents,
exposing related metadata and taxonomies as required, enabling the citizen portal to
search through the publications.

GPP-publicatiebank is required to manage the actual publications and ensure
they get indexed (or retracted if needed).

API specification
=================

|oas|

==============  ==============  =============================
Version         Release date    API specification
==============  ==============  =============================
latest          n/a             `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/GPP-Woo/GPP-zoeken/main/src/woo_search/api/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/GPP-Woo/GPP-zoeken/main/src/woo_search/api/openapi.yaml>`_,
                                (`changes <https://github.com/GPP-Woo/GPP-zoeken/compare/2.0.0..main>`_)
1.1.1           2024-07-10      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/GPP-Woo/GPP-zoeken/2.0.0/src/woo_search/api/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/GPP-Woo/GPP-zoeken/2.0.0/src/woo_search/api/openapi.yaml>`_
1.1.0           2024-05-20      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/GPP-Woo/GPP-zoeken/2.0.0-rc.0/src/woo_search/api/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/GPP-Woo/GPP-zoeken/2.0.0-rc.0/src/woo_search/api/openapi.yaml>`_
1.0.0           2024-03-26      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/GPP-Woo/GPP-zoeken/1.0.0/src/woo_search/api/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/GPP-Woo/GPP-zoeken/1.0.0/src/woo_search/api/openapi.yaml>`_
==============  ==============  =============================

See: `All versions and changes <https://github.com/GPP-Woo/GPP-zoeken/blob/main/CHANGELOG.rst>`_


Developers
==========

|build-status| |coverage| |ruff| |docker| |python-versions|

This repository contains the source code for GPP-zoeken. To quickly
get started, we recommend using the Docker image. You can also build the
project from the source code. For this, please look at `INSTALL.rst <INSTALL.rst>`_.

Quickstart
----------

1. Download and run GPP-zoeken:

   .. code:: bash

      wget https://raw.githubusercontent.com/GPP-Woo/GPP-zoeken/main/docker-compose.yml
      docker-compose up -d --no-build

2. In the browser, navigate to ``http://localhost:8000/`` to access the admin
   and the API. You can log in with the ``admin`` / ``admin`` credentials.


References
==========

* `Documentation <https://gpp-zoeken.readthedocs.io>`_
* `Docker image <https://hub.docker.com/r/maykinmedia/woo-search>`_
* `Issues <https://github.com/GPP-Woo/GPP-zoeken/issues>`_
* `Code <https://github.com/GPP-Woo/GPP-zoeken>`_
* `Community <https://github.com/GPP-Woo>`_


License
=======

Copyright © Maykin 2024

Licensed under the EUPL_


.. _`Nederlandse versie`: README.rst

.. _`Maykin B.V.`: https://www.maykinmedia.nl

.. _`EUPL`: LICENSE.md

.. |build-status| image:: https://github.com/GPP-Woo/GPP-zoeken/actions/workflows/ci.yml/badge.svg
    :alt: Build status
    :target: https://github.com/GPP-Woo/GPP-zoeken/actions/workflows/ci.yml

.. |docs| image:: https://readthedocs.org/projects/gpp-zoeken/badge/?version=latest
    :target: https://gpp-zoeken.readthedocs.io/
    :alt: Documentation Status

.. |coverage| image:: https://codecov.io/github/GPP-Woo/GPP-zoeken/branch/main/graphs/badge.svg?branch=main
    :alt: Coverage
    :target: https://codecov.io/gh/GPP-Woo/GPP-zoeken

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Ruff

.. |docker| image:: https://img.shields.io/docker/v/maykinmedia/woo-search?sort=semver
    :alt: Docker image
    :target: https://hub.docker.com/r/maykinmedia/woo-search

.. |python-versions| image:: https://img.shields.io/badge/python-3.12%2B-blue.svg
    :alt: Supported Python version

.. |oas| image:: https://github.com/GPP-Woo/GPP-zoeken/actions/workflows/oas.yml/badge.svg
    :alt: OpenAPI specification checks
    :target: https://github.com/GPP-Woo/GPP-zoeken/actions/workflows/oas.yml
