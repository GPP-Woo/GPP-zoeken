==========
GPP-zoeken
==========

:Version: 2.1.0
:Source: https://github.com/GPP-Woo/GPP-zoeken
:Keywords: WOO, Openbare Documenten, NL, Open Data

|docs| |docker|

Een zoek-component die voorziet in een "Openbare documenten"-index.

(`English version`_)

Ontwikkeld door `Maykin B.V.`_ in opdracht ICATT en Dimpact.

Introductie
===========

De `Wet Open Overheid <https://www.rijksoverheid.nl/onderwerpen/wet-open-overheid-woo>`_
vereist dat overheidsorganisaties actief documenten openbaar maken zodat deze door
geïnteresseerde partijen ingezien kunnen worden. Dimpact voorziet in een Generiek
Publicatieplatform om dit mogelijk te maken voor gemeenten, waarvan de openbare
documentenregistratiecomponent een onderdeel vormt.

GPP-zoeken maakt het mogelijk om openbaar gemaakte documenten te indexeren en
doorzoeken, waarbij de gerelateerde metadata en indelingen aangeboden worden.
Burgerportalen kunnen hiermee de zoekfunctie aanbieden om publicaties te doorzoeken.

GPP-publicatiebank is vereist om de publicaties te beheren en aan te bieden
(of in te trekken) aan GPP-zoeken zodat ze daadwerkelijk geïndexeerd worden.


API specificatie
================

|oas|

==============  ==============  =============================
Versie          Release datum   API specificatie
==============  ==============  =============================
latest          n/a             `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/GPP-Woo/GPP-zoeken/main/src/woo_search/api/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/GPP-Woo/GPP-zoeken/main/src/woo_search/api/openapi.yaml>`_,
                                (`verschillen <https://github.com/GPP-Woo/GPP-zoeken/compare/2.1.0-rc.0..main>`_)
1.2.0           2025-07-16      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/GPP-Woo/GPP-zoeken/2.1.0-rc.0/src/woo_search/api/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/GPP-Woo/GPP-zoeken/2.1.0-rc.0/src/woo_search/api/openapi.yaml>`_                                (`verschillen <https://github.com/GPP-Woo/GPP-zoeken/compare/2.0.0..main>`_)
1.1.1           2024-07-10      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/GPP-Woo/GPP-zoeken/2.0.0/src/woo_search/api/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/GPP-Woo/GPP-zoeken/2.0.0/src/woo_search/api/openapi.yaml>`_
1.1.0           2024-05-20      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/GPP-Woo/GPP-zoeken/2.0.0-rc.0/src/woo_search/api/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/GPP-Woo/GPP-zoeken/2.0.0-rc.0/src/woo_search/api/openapi.yaml>`_
1.0.0           2024-03-26      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/GPP-Woo/GPP-zoeken/1.0.0/src/woo_search/api/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/GPP-Woo/GPP-zoeken/1.0.0/src/woo_search/api/openapi.yaml>`_
==============  ==============  =============================

Zie: `Alle versies en wijzigingen <https://github.com/GPP-Woo/GPP-zoeken/blob/main/CHANGELOG.rst>`_


Ontwikkelaars
=============

|build-status| |coverage| |ruff| |docker| |python-versions|

Deze repository bevat de broncode voor GPP-zoeken. Om snel aan de slag
te gaan, raden we aan om de Docker image te gebruiken. Uiteraard kan je ook
het project zelf bouwen van de broncode. Zie hiervoor `INSTALL.rst <INSTALL.rst>`_.

Quickstart
----------

1. Download en start GPP-zoeken:

   .. code:: bash

      wget https://raw.githubusercontent.com/GPP-Woo/GPP-zoeken/main/docker-compose.yml
      docker-compose up -d --no-build

2. In de browser, navigeer naar ``http://localhost:8000/`` om de beheerinterface
   en de API te benaderen, waar je kan inloggen met ``admin`` / ``admin``.


Links
=====

* `Documentatie <https://gpp-zoeken.readthedocs.io>`_
* `Docker image <https://hub.docker.com/r/maykinmedia/woo-search>`_
* `Issues <https://github.com/GPP-Woo/GPP-zoeken/issues>`_
* `Code <https://github.com/GPP-Woo/GPP-zoeken>`_
* `Community <https://github.com/GPP-Woo>`_


Licentie
========

Copyright © Maykin 2024

Licensed under the EUPL_


.. _`English version`: README.EN.rst

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
