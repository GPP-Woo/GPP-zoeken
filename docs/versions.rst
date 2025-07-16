.. _versions:

Versioning
==========

Policy
------

GPP-zoeken (and the associated API spefication) adheres to
`semantic versioning <https://semver.org/>`_, meaning major versions may introduce
breaking changes and minor versions are backwards compatible. Release notes for each
version are documented in the :ref:`changelog`.

The version of the backend and its API specification are not guaranteed to be the same -
bugfixes and improvements can result in a newer version of the backend compared to the
shipped API specification. A version bump in the API specification always implies a
version bump of the backend.

Backend and API
---------------

The backend contains the storage and exposes the API.

.. table:: API version offered by backend version
   :widths: auto

   =============== ===========
   Backend version API version
   =============== ===========
   2.1.0           1.2.0
   2.0.0           1.1.0
   1.0.0           1.0.0
   =============== ===========

Compatibility and requirements
------------------------------

GPP-zoeken itself makes use of other services, APIs and software. The tables
below describe these dependencies.

GPP-publicatiebank or equivalent alternative
********************************************

GPP-zoeken downloads binary file contents if configured to do so - it fetches the
download URL it has been provided. The table below lists confirmed support, but any
:ref:`service <configuration_services>` that offers binary downloads should be
compatible.

.. table:: GPP-pulicatiebank support
   :widths: auto

   ======================  ===========
   GPP-Publicatiebank API  Status
   ======================  ===========
   v2.x                    Supported
   v1.x                    Supported
   ======================  ===========

PostgreSQL
**********

PostgreSQL is the database used. PostgreSQL 13 and newer are supported.

.. table:: PostgreSQL version support
   :widths: auto

   =============  ==========================
   PostgreSQL     Status
   =============  ==========================
   17             Should work
   16             Automatically tested in CI
   15             Supported
   14             Supported
   =============  ==========================

Redis
*****

Redis is a key-value store used for caching purposes. Redis 5 and newer are supported.
Valkey (a Redis fork) should also work.

.. table:: Redis version support
   :widths: auto

   =============  ==========================
   Redis          Status
   =============  ==========================
   8              Should work
   7              Supported (tested via docker compose)
   6              Automatically tested in CI
   5              Should work
   =============  ==========================

Elastic Search
**************

Metadata and document contents are indexed in Elastic Search.

.. table:: Elastic Search version support
   :widths: auto

   ==============  ==========================
   Elastic Search  Status
   ==============  ==========================
   8.x             Should work
   8.17.x          Tested in CI
   ==============  ==========================
