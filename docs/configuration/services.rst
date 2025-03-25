.. _configuration_services:

Services
========

GPP-zoeken is designed to operate in a micro-service environment, which broadly
means that it talks to other APIs to be able to function correctly - see
:ref:`installation_requirements` for some more background information and things that
need to be arranged in those external services.

The services configuration in GPP-zoeken stores the connection and
authentication details for those external services.

General instructions
--------------------

To view and manage services, navigate to **Admin** > **Configuration** > **Services**.

The list shows an overview of configured services, displaying the label/name, the kind
of service and the base URL where it is hosted.

In the top right of the page, you can click the **Service toevoegen** button to add a
new service. To edit an existing service, click its label, which takes you to the
edit page.

GPP-publicatiebank configuration
--------------------------------

GPP-zoeken depends on the `GPP-Publicatiebank <https://gpp-publicatiebank.readthedocs.io/>`_
service to retrieve the contents of referenced documents. A service needs to be
configured for this. If no service is configured, indexing the content of a document will be skipped.

What you'll need
~~~~~~~~~~~~~~~~

* The API root URL, e.g. ``https://gpp-publicatiebank.example.com/api/v1/``
* API credentials, typically a token: e.g. ``fbee1a6a1d07a43ef82b9ebd18a3520722b447e8``

Configuration in the registration component
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Navigate to the **Admin** environment.
2. In the menu, navigate to **Configuration** > **Services**.
3. Click the **Add service** button in the top right of the screen.
4. Fill out the form fields:

    - ``Label``: a label so you can recognize the service in a choice list, e.g. "GPP-Publicatiebank".
    - ``Type``: select "ORC (Overige)"
    - ``API root URL``: enter the obtained base URL of the API, e.g.
      ``https://gpp-publicatiebank.example.com/api/v1/`` from the examples in the previous
      section.
    - ``Authorization type``: select "API key"
    - ``Header key`` enter ``Authorization``
    - ``Header value``: enter ``Token <token value>``, for example
      ``Token fbee1a6a1d07a43ef82b9ebd18a3520722b447e8``.

5. Save the changes.
