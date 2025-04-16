=============
Release notes
=============

1.1.0 (2025-??-??)
==================

(unreleased)

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

