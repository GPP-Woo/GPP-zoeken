==========
WOO Search
==========

:Version: 0.1.0
:Source: https://github.com/GeneriekPublicatiePlatformWoo/search
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

This search component makes it possible to index and search published documents,
exposing related metadata and taxonomies as required, enabling the citizen portal to
search through the publications.

A registration component (ODRC) is required to manage the actual publications and ensure
they get indexed (or retracted if needed).

API specification
=================

|oas|

==============  ==============  =============================
Version         Release date    API specification
==============  ==============  =============================
latest          n/a             `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/GeneriekPublicatiePlatformWoo/search/main/src/woo_search/api/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/GeneriekPublicatiePlatformWoo/search/main/src/woo_search/api/openapi.yaml>`_,
                                (`verschillen <https://github.com/GeneriekPublicatiePlatformWoo/search/compare/0.1.0..main#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
0.1.0           YYYY-MM-DD      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/GeneriekPublicatiePlatformWoo/search/0.1.0/src/woo_search/api/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/GeneriekPublicatiePlatformWoo/search/0.1.0/src/woo_search/api/openapi.yaml>`_
==============  ==============  =============================

See: `All versions and changes <https://github.com/GeneriekPublicatiePlatformWoo/search/blob/main/CHANGELOG.rst>`_


Developers
==========

|build-status| |coverage| |black| |docker| |python-versions|

This repository contains the source code for the search component. To quickly
get started, we recommend using the Docker image. You can also build the
project from the source code. For this, please look at `INSTALL.rst <INSTALL.rst>`_.

Quickstart
----------

1. Download and run woo-search:

   .. code:: bash

      wget https://raw.githubusercontent.com/GeneriekPublicatiePlatformWoo/search/main/docker-compose.yml
      docker-compose up -d --no-build

2. In the browser, navigate to ``http://localhost:8000/`` to access the admin
   and the API. You can log in with the ``admin`` / ``admin`` credentials.


References
==========

* `Documentation <https://gpp-zoeken.readthedocs.io>`_
* `Docker image <https://hub.docker.com/r/maykinmedia/woo-search>`_
* `Issues <https://github.com/GeneriekPublicatiePlatformWoo/search/issues>`_
* `Code <https://github.com/GeneriekPublicatiePlatformWoo/search>`_
* `Community <https://github.com/GeneriekPublicatiePlatformWoo>`_


License
=======

Copyright © Maykin 2024

Licensed under the EUPL_


.. _`Nederlandse versie`: README.rst

.. _`Maykin B.V.`: https://www.maykinmedia.nl

.. _`EUPL`: LICENSE.md

.. |build-status| image:: https://github.com/GeneriekPublicatiePlatformWoo/search/actions/workflows/ci.yml/badge.svg
    :alt: Build status
    :target: https://github.com/GeneriekPublicatiePlatformWoo/search/actions/workflows/ci.yml

.. |docs| image:: https://readthedocs.org/projects/gpp-zoeken/badge/?version=latest
    :target: https://gpp-zoeken.readthedocs.io/
    :alt: Documentation Status

.. |coverage| image:: https://codecov.io/github/GeneriekPublicatiePlatformWoo/search/branch/main/graphs/badge.svg?branch=main
    :alt: Coverage
    :target: https://codecov.io/gh/GeneriekPublicatiePlatformWoo/search

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: Code style
    :target: https://github.com/psf/black

.. |docker| image:: https://img.shields.io/docker/v/maykinmedia/woo-search?sort=semver
    :alt: Docker image
    :target: https://hub.docker.com/r/maykinmedia/woo-search

.. |python-versions| image:: https://img.shields.io/badge/python-3.12%2B-blue.svg
    :alt: Supported Python version

.. |oas| image:: https://github.com/GeneriekPublicatiePlatformWoo/search/actions/workflows/oas.yml/badge.svg
    :alt: OpenAPI specification checks
    :target: https://github.com/GeneriekPublicatiePlatformWoo/search/actions/workflows/oas.yml
