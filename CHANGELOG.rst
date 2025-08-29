=============
Release notes
=============

2.1.0 (2025-09-01)
==================

Upgrade procedure
-----------------

.. warning:: Manual intervention required.

    The elastic search mappings are updated to store the publication date (``gepubliceerd_op``) of
    documents, publications and topics (which is a carbon copy of the ``registratiedatum`` as a convenience field)
    To make sure that this new property contains the ``registratiedatum`` of existing indexed documents either:

    * re-index them from the GPP-publicatiebank (version 2.0.0 or newer)
    * or run the migration script in the container:

        .. code-block:: bash

            python /app/src/manage.py sync_publication_date

Features
--------

* [#100] Added more date fields to publication, document and topic search documents.
  All three documents gain the field ``gepubliceerd_op`` and the publication document
  additionally gains the fields ``datum_begin_geldigheid`` and ``datum_einde_geldigheid``.
  You can now also query/filter on these fields in the search endpoint.
* [#101] Chronological ordering of search results is now done on the ``gepubliceerd_op`` field
   rather than ``laatst_gewijzigd_datum``.

2.1.0-rc.0 (2025-07-16)
=======================

Upgrade procedure
-----------------

.. warning:: Manual intervention required.

    The elastic search mappings are updated to store the identifiers ("kenmerken") of
    documents and publications together. To make sure that this new property contains
    the ``identifier`` of existing indexed documents, either:

    * re-index them from the GPP-publicatiebank
    * or run the migration script in the container:

        .. code-block:: bash

            python /app/src/manage.py sync_identifiers

Deprecations
------------

* [#31] The ``identifier`` field is now deprecated, use the ``identifiers`` array instead.

Bugfixes
--------

* [#81] Ensure that zip files with contents that exceed the filesize limit still get partially indexed,
  up to the total file size limit.

Project maintenance
-------------------

* Replaced boilerplate utilities with their equivalents from maykin-common.
* Updated "supported versions" documentation section.
* Upgraded some dependencies to their latest available versions.

2.0.0 (2025-07-10)
==================

Definitive stable release.

The release candidate did not reveal any issues, so we turned it into a stable release.

Upgrade procedure
-----------------

.. warning:: Manual intervention required.

    After deploying this version, the index mappings in Elastic Search need to be
    updated to support topics. We don't have an automated procedure for this yet. The
    easiest way to do this, is by deleting and re-creating the indices, and then
    re-index the data from GPP-publicatiebank (version 1.1.0 or newer).

    .. code-block:: http

        DELETE https://my-elastic.example.com/document HTTP/1.1

    .. code-block:: http

        DELETE https://my-elastic.example.com/publication HTTP/1.1

    where ``document`` and ``publication`` are the names of the indices we manage.

    Then, open an interactive shell for GPP-zoeken (with ``kubectl exec`` or
    ``docker exec``), and run:

    .. code-block:: bash

        python src/manage.py initialize_mappings --wait

    You should then get output confirming the indices have been re-created.

Breaking changes
----------------

* Dropped PostgreSQL 13 support (our underlying framework doesn't support it anymore).
* The index mappings need to be dropped and re-created, see the upgrade procedure above.

Features
--------

* [#76, #43] Added "Topics" as resource type to group multiple publications together.
* [#63] Added support for indexing ZIP (``.zip`` and ``.7z``) files. The archives are
  now extracted and the content of the extracted files is indexed and searchable.

Project maintenance
-------------------

* Switched code quality tools to Ruff.
* Simplified documentation test tools.
* Added upgrade-check mechanism for "hard stops".
* Upgraded framework version to next LTS release.
* Addressed API schema linter error for URL-value defaults.

2.0.0-rc.0 (2025-05-19)
=======================

Upgrade procedure
-----------------

.. warning:: Manual intervention required.

    After deploying this version, the index mappings in Elastic Search need to be
    updated to support topics. We don't have an automated procedure for this yet. The
    easiest way to do this, is by deleting and re-creating the indices, and then
    re-index the data from GPP-publicatiebank (version 1.1.0 or newer).

    .. code-block:: http

        DELETE https://my-elastic.example.com/document HTTP/1.1

    .. code-block:: http

        DELETE https://my-elastic.example.com/publication HTTP/1.1

    where ``document`` and ``publication`` are the names of the indices we manage.

    Then, open an interactive shell for GPP-zoeken (with ``kubectl exec`` or
    ``docker exec``), and run:

    .. code-block:: bash

        python src/manage.py initialize_mappings --wait

    You should then get output confirming the indices have been re-created.

Breaking changes
----------------

* Dropped PostgreSQL 13 support (our underlying framework doesn't support it anymore).
* The index mappings need to be dropped and re-created, see the upgrade procedure above.

Features
--------

* [#76, #43] Added "Topics" as resource type to group multiple publications together.
* [#63] Added support for indexing ZIP (``.zip`` and ``.7z``) files. The archives are
  now extracted and the content of the extracted files is indexed and searchable.

Project maintenance
-------------------

* Switched code quality tools to Ruff.
* Simplified documentation test tools.
* Added upgrade-check mechanism for "hard stops".
* Upgraded framework version to next LTS release.

1.0.0 (2025-04-16)
==================

The release candidate is now released as stable version.

There are no changes compared to release candidate 1 - see the changelog entry below.

1.0.0-rc.0 (2025-03-26)
=======================

We proudly announce the first release candidate of GPP-zoeken!

The 1.0 version of this component is ready for production. It provides the necessary
functionality to provide your organisation-specific search index of public documents.

Features
--------

* Admin panel for technical and functional administrators
    - Manage API clients and user accounts.
    - Configure connections to external services, like the GPP-publicatiebank and OpenID
      Connect provider.
* JSON API for indexing, deleting and searching publications and documents
  to/from Elasticsearch, with the ability to search through the text contents of files.
* OpenID Connect or local user account with MFA authentication options for the admin
  panel.
* Extensive documentation, from API specification to (admin) user manual.

