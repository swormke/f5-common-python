Creating the Collection Objects
===============================

.. note::

This guide uses the LTM data-group object as its example.  This object
can be accessed via the REST API at the following URI:
``https://192.168.1.1/mgmt/tm/ltm/data-group``

GET the JSON for the Object
~~~~~~~~~~~~~~~~~~~~~~~~~~~
In order to figure out what we need to do for this object we need to get
the JSON for the object from the BIG-IP.

.. code::

    $ curl -k -u admin:admin https://host-vm-15/mgmt/tm/ltm/data-group
    {"kind":"tm:ltm:data-group:data-groupcollectionstate","selfLink":"https://localhost/mgmt/tm/ltm/data-group?ver=11.6.0","items":[{"reference":{"link":"https://localhost/mgmt/tm/ltm/data-group/external?ver=11.6.0"}},{"reference":{"link":"https://localhost/mgmt/tm/ltm/data-group/internal?ver=11.6.0"}}]}

Take note of the ``kind`` attribute, it helps us figure out what kind of
object to make.  In this case it ends in the string ``collectionstate`` which
means we need to create a :class:`~f5.bigip.resource.Collection` class.

It is important to remember the following about collections:

#. Collections are named after their REST endpoint.
#. Collections always end in ``s``.  If the object already ends in ``s`` we add
   ``_s`` to the collection name.
#. Collections always have a kind that ends in ``collectionstate``.
#. Collections generally cannot be created, updated, or deleted.

.. note::

   The JSON returned for the data-group collection has an ``items`` attribute
   in it which means that it has collections below it as well.  If an object
   has no ``items`` attribute it only contains ``Resource`` objects below it.

Create the Module
~~~~~~~~~~~~~~~~~
As we can see from the URL this collection object is found under the
LTM :mod:`~f5.bigip.resource.OrganizingCollection`.  This means that we need
to create a sub-module for the :mod:`f5.bigip.ltm` module.  We do this by
adding a file to the ``f5-common-python/f5/bigip/ltm/`` directory that has
the same name as the collection that we are creating.  In this case we call
that file ``data_group.py``.

.. warning::

    Because the ``-`` is not allowed in module and class names in Python we
    substitute it with ``_``.

Inside this file we add the required Apache v2.0 header, our sub-module doc
strings and our import statements.

.. code:: python

    # Copyright 2016 F5 Networks Inc.
    #
    # Licensed under the Apache License, Version 2.0 (the "License");
    # you may not use this file except in compliance with the License.
    # You may obtain a copy of the License at
    #
    #    http://www.apache.org/licenses/LICENSE-2.0
    #
    # Unless required by applicable law or agreed to in writing, software
    # distributed under the License is distributed on an "AS IS" BASIS,
    # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    # See the License for the specific language governing permissions and
    # limitations under the License.
    #

    """BIG-IP Local Traffic Manager (LTM) data-group module.

    REST URI
        ``http://localhost/mgmt/tm/ltm/data-group``

    GUI Path
        ``Local Traffic --> Snat``

    REST Kind
        ``tm:ltm:data-group:*``
    """

    from f5.bigip.resource import Collection

Create the Collection Class
~~~~~~~~~~~~~~~~~~~~~~~~~~~
We first need to create the collection object that will allow us to access
the Resources contained by the collection.  We do this by adding a class
that inherits from the :class:`f5.bigip.resource.Collection` class.  This
class has the same name as the REST URI endpoint, but ends in the letter ``s``.

.. note::

   We know that data-group is a collection because its JSON kind is
   ``tm:ltm:data-group:data-groupcollectionstate`` which ends in
   ``collectionstate``

.. code:: python

    class Data_Groups(Collection):
        """BIG-IP LTM Data Group collection"""
        def __init__(self, ltm):
            super(data_groups, self).__init__(ltm)
            self._meta_data['allowed_lazy_attributes'] = []
            self._meta_data['attribute_registry'] = {}

There are a few important things to take note of in the code above.

ltm Container
^^^^^^^^^^^^^
In line 3 you see that the ``__init__`` takes a parameter named ``ltm``.  This
is called the containing object which is the object that you *dot* through to
get to this object. In other words it is the module that we are a sub-module
of.  All Collections need this to be passed in and follow this pattern.

``_meta_data`` Dictionary
^^^^^^^^^^^^^^^^^^^^^^^^^
The ``_meta_data`` dictionary holds information about the container.  In this
case the two items in this dictionary that are currently empty are very
important and will be added to when we create the resources for this object.

allowed_lazy_attributes:
  These are the objects that you will be able to *dot* down to under this
  collection.  This is generally the resource objects that we will define
  in later steps.  But for now this is the objects that will get created when
  you do something like ``f5.bigip.ltm.data_groups.foo``. In this case we would
  add ``Foo`` to that list.  If a call tries to use anything other than one
  of the objects in this list they will get an
  :exc:`~f5.bigip.mixins.AllowedLazyAttributes` exception.

attribute_registry:
  This is a dictionary in which the key is the ``kind`` of the lazy attributes
  and the value is the Object they represent.  Again we will see this later
  when we add the ``Resource`` objects.


Update the Lazy Attributes of the OrganizingCollection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Import the new ``Collection`` class and add it to it's container's lazy
attributes.  In this case the OrganizingCollection is ltm so the changes
need to be in the ``f5/bigip/ltm/__init__.py`` file.

.. code::

    from f5.bigip.ltm.data_group import Data_Groups


    class Ltm(OrganizingCollection):
        """BIG-IP® Local Traffic Manager (LTM) organizing collection."""
        def __init__(self, bigip):
            super(Ltm, self).__init__(bigip)
            self._meta_data['allowed_lazy_attributes'] = [
                Monitor,
                Nats,
                ...
                Data_Groups,
            ]

Update the ``_meta_data`` Dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. note::

    Most ``Collection`` objects do not need this step.  The data-group URI
    has a ``-`` in it which was substituted for an ``_`` and therefore will
    not match the auto-generated URI which uses the class name to construct it.

One of the entries in the ``_meta_data`` dictionary is named ``uri``.  This
holds the URI that the SDK can use to access this object.  The reason we put
it in the ``_meta_data`` is because the BIG-IP returns the ``selfLink`` to us
with ``localhost`` as the device's hostname instead of its actual FQDN or IP
address. Because we only store attributes returned to us in the JSON as
class attributes we modify the ``selfLink`` to replace the localhost string
with the actual hostname/IP address and store it in the ``_meta_data`` for
the class.

To override the URI we simply add the following line to the end of our
constructor.

.. code::

    self._meta_data['uri'] = self._meta_data['uri'].replace('_', '-')


Creating the Sub-Collections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    For collections that do not have the ``items`` attributes you can skip
    this step and go onto the :doc:`resource` section.

Because the JSON returned for the data-group URI has an ``items`` attribute
in it we need to create the additional ``Collection`` objects that are
in that list and add them as ``allowed_lazy_attributes`` and register their
attributes in the ``Data_Groups`` object.

Getting the Sub-Collections JSON
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The URI for the sub-collections can be found in the JSON returned by the
data-group.  In this case we have the following sub-collections to work on.

* external (``https://localhost/mgmt/tm/ltm/data-group/external?ver=11.6.0``)
* internal (``https://localhost/mgmt/tm/ltm/data-group/internal?ver=11.6.0``)

We can get their JSON by replacing localhost with the hostname/IP address
of our BIG-IP.

.. code:: shell

    $> curl -k -u admin:admin https://host-vm-15/mgmt/tm/ltm/data-group/external?ver=11.6.0
    {"kind":"tm:ltm:data-group:external:externalcollectionstate","selfLink":"https://localhost/mgmt/tm/ltm/data-group/external?ver=11.6.0"}
    $> curl -k -u admin:admin https://host-vm-15/mgmt/tm/ltm/data-group/internal?ver=11.6.0
    {"kind":"tm:ltm:data-group:internal:internalcollectionstate","selfLink":"https://localhost/mgmt/tm/ltm/data-group/internal?ver=11.6.0","items":[{"kind":"tm:ltm:data-group:internal:internalstate","name":"aol","partition":"Common","fullPath":"/Common/aol","generation":1,"selfLink":"https://localhost/mgmt/tm/ltm/data-group/internal/~Common~aol?ver=11.6.0","type":"ip","records":[{"name":"64.12.96.0/19"},{"name":"195.93.16.0/20"},{"name":"195.93.48.0/22"},{"name":"195.93.64.0/19"},{"name":"195.93.96.0/19"},{"name":"198.81.0.0/22"},{"name":"198.81.8.0/23"},{"name":"198.81.16.0/20"},{"name":"202.67.65.128/25"},{"name":"205.188.112.0/20"},{"name":"205.188.146.144/30"},{"name":"205.188.192.0/20"},{"name":"205.188.208.0/23"},{"name":"207.200.112.0/21"}]},{"kind":"tm:ltm:data-group:internal:internalstate","name":"images","partition":"Common","fullPath":"/Common/images","generation":1,"selfLink":"https://localhost/mgmt/tm/ltm/data-group/internal/~Common~images?ver=11.6.0","type":"string","records":[{"name":".bmp"},{"name":".gif"},{"name":".jpg"}]},{"kind":"tm:ltm:data-group:internal:internalstate","name":"private_net","partition":"Common","fullPath":"/Common/private_net","generation":1,"selfLink":"https://localhost/mgmt/tm/ltm/data-group/internal/~Common~private_net?ver=11.6.0","type":"ip","records":[{"name":"10.0.0.0/8"},{"name":"172.16.0.0/12"},{"name":"192.168.0.0/16"}]}]}

Creating the Sub-Collection Objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Using this JSON we can build the new collection objects just like we did above.

.. code:: python

    class Externals(Collection):
        """BIG-IP LTM Data Group external collection"""
        def __init__(self, data_groups):
            super(data_groups, self).__init__(data_groups)
            self._meta_data['allowed_lazy_attributes'] = []
            self._meta_data['attribute_registry'] = {}


    class Internals(Collection):
        """BIG-IP LTM Data Group internal collection"""
        def __init__(self, data_groups):
            super(data_groups, self).__init__(data_groups)
            self._meta_data['allowed_lazy_attributes'] = []
            self._meta_data['attribute_registry'] = {}

Notice that our container object is now ``data_groups`` instead of ``ltm``
because these are under the data_groups path.

Adding the Sub-Collections to the Container's _meta_data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Because these two new sub-collections are accessed via the path
``f5.bigip.ltm.data_groups`` we must add them as ``allowed_lazy_attributes``
and register their kind.

The code for the ``Data_Groups`` class is now

.. code::

    class Data_Groups(Collection):
    """BIG-IP LTM Data Group collection"""
    def __init__(self, ltm):
        super(data_groups, self).__init__(ltm)
        self._meta_data['allowed_lazy_attributes'] = [External, Internal]
        self._meta_data['attribute_registry'] = {
            'tm:ltm:data-group:external:externalcollectionstate': External,
            'tm:ltm:data-group:internal:internalcollectionstate': Internal,
        }
        self._meta_data['uri'] = self._meta_data['uri'].replace('_', '-')


File Contents
~~~~~~~~~~~~~
At this point the ``data_groups.py`` file should contain the following.

.. code:: python

    # Copyright 2016 F5 Networks Inc.
    #
    # Licensed under the Apache License, Version 2.0 (the "License");
    # you may not use this file except in compliance with the License.
    # You may obtain a copy of the License at
    #
    #    http://www.apache.org/licenses/LICENSE-2.0
    #
    # Unless required by applicable law or agreed to in writing, software
    # distributed under the License is distributed on an "AS IS" BASIS,
    # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    # See the License for the specific language governing permissions and
    # limitations under the License.
    #

    """BIG-IP Local Traffic Manager (LTM) data-group module.

    REST URI
        ``http://localhost/mgmt/tm/ltm/data-group``

    GUI Path
        ``N/A``

    REST Kind
        ``tm:ltm:data-group:*``
    """

    from f5.bigip.resource import Collection


    class Data_Groups(Collection):
        """BIG-IP LTM Data Group collection"""
        def __init__(self, ltm):
            super(data_groups, self).__init__(ltm)
            self._meta_data['allowed_lazy_attributes'] = [External, Internal]
            self._meta_data['attribute_registry'] = {
                'tm:ltm:data-group:external:externalcollectionstate': External,
                'tm:ltm:data-group:internal:internalcollectionstate': Internal,
            }
            self._meta_data['uri'] = self._meta_data['uri'].replace('_', '-')


    class Externals(Collection):
        """BIG-IP LTM Data Group external collection"""
        def __init__(self, data_groups):
            super(data_groups, self).__init__(data_groups)
            self._meta_data['allowed_lazy_attributes'] = []
            self._meta_data['attribute_registry'] = {}


    class Internals(Collection):
        """BIG-IP LTM Data Group internal collection"""
        def __init__(self, data_groups):
            super(data_groups, self).__init__(data_groups)
            self._meta_data['allowed_lazy_attributes'] = []
            self._meta_data['attribute_registry'] = {}

Simple Test
~~~~~~~~~~~
At this point we should be able to test our collection object with a few
simple commands and verify that we see the ``_meta_data['uri']`` set correctly
and that we have a :class:`f5.bigip.ltm.Ltm` object as our container.
The same for ``Internals`` and ``Externals``, they should have ``Data_Groups``
as their container.

.. code:: python

    >>> from f5.bigip import BigIP
    >>> bigip = BigIP('192.168.1.1', 'admin', 'admin')
    >>> dg = bigip.ltm.data_groups
    >>> dg.raw
    >>> i = bigip.ltm.data_groups.internals
    >>> i.raw
    >>> e = bigip.ltm.data_groups.externals
    >>> e.raw

It's also not a bad time to run ``flake8`` on the file and fix any of the
errors it may generate.

.. code:: shell

   $> flake8 f5/bigip/ltm/data_group.py
