.. _introduction_index:

Introduction
============

The Dutch government wishes to be open and transparent to its citizens. To achieve this,
the law `Wet open overheid (Woo)`_ was established,
requiring government organisations to actively and digitally publish their documents and thus create *public records*.

To support govenment organisations in executing this law, the "Generic Publications Platform Woo (GPP-Woo)" was developed.
This platform is an aggregation of four components, including the 'GPP-Zoeken' component.
This component provides a search index and JSON API to index and (fuzzy) search public
records including their metadata.

For a full publication platform, three additional components are required:

* `GPP App <https://github.com/GPP-Woo/GPP-app>`_, a component which provides public servants with a web-based user interface to manulaly upload and publish public records.
* `GPP Publicatiebank <https://github.com/GPP-Woo/GPP-publicatiebank>`_, a component responsible for public record storage and publishing workflows.
* `GPP Citizen Portal <https://github.com/GPP-Woo/GPP-burgerportaal>`_, a component which provides citizens with a website where they can browse and search through public records.

All components are designed in line with the `Common Ground`_ model.

This project is and only uses :ref:`introduction_open-source`.


.. toctree::
   :maxdepth: 1
   :caption: Further reading

   team
   open-source/index

.. _`Wet open overheid (Woo)` : https://wetten.overheid.nl/BWBR0045754/
.. _`Common Ground`: https://commonground.nl/
