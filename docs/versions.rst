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
   1.0.0           1.0.0
   =============== ===========

Compatibility and requirements
------------------------------

GPP-zoeken itself makes use of other services, APIs and software. The tables
below describe these dependencies.

PostgreSQL
**********

PostgreSQL is the database used. PostgreSQL 13 and newer are supported.

.. table:: PostgreSQL version support
   :widths: auto

   =============  ==========================
   PostgreSQL     Status
   =============  ==========================
   13             Supported
   14             Supported
   15             Supported
   16             Automatically tested in CI
   =============  ==========================

Redis
*****

Redis is a key-value store used for caching purposes. Redis 5 and newer are supported.

.. table:: Redis version support
   :widths: auto

   =============  ==========================
   Redis          Status
   =============  ==========================
   5              Should work
   6              Automatically tested in CI
   7              Supported (tested via docker compose)
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
