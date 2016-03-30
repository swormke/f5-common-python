Developer Guide
===============

This guide is intended for use by Python developers who are contributing
code and new resources to the project.  It will help you understand how to
create new :mod:`~f5.bigip.resource.Collection` and
:mod:`~f5.bigip.resource.Resource` objects for BIG-IP configuration that is
not already included in the SDK.

For the purposes of this tutorial we will outline the steps for creating
a new set of collections and resources for the LTM data-group collection which
is found at the iControl REST URI ``https://192.168.1.1/mgmt/tm/ltm/data-group``.

.. toctree::
    :maxdepth: 1

    setup
    collection
    resource
    tests
    docs
    pullrequest


Prerequisites
~~~~~~~~~~~~~
Before starting to contribute we are going to assume you are familiar with
the following topics.

* You have read the :doc:`../userguide/index`, and understand the basic
  concepts of ``Collection`` and ``Resource`` objects.
* You have used the SDK to create and manipulate objects on the BIG-IP.
* You have read the BIG-IP iControl REST user guide
* You understand Python classes, inheritance, and mix-ins.
* You have installed and know how to use pip, the Python package manager
* You have installed and understand how to use virtual-environments
* You have access to a BIG-IP for testing and know how to interact with the
  iControl REST API in a way that you can get JSON responses from the
  various URI paths you would like to implement
