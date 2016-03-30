Creating the Resource Objects
=============================
After the ``Collection`` objects are created we can add the ``Resource``
objects and add them to their container's ``allowed_lazy_attributes`` and
register their kind.

.. note::

   Resource objects' JSON ``kind`` attribute does not end in ``collectionstate``
   and most often ends in the name of the resource with the string 'state' at
   the end.  For example ``internalstate``.

Get the Resource's JSON
~~~~~~~~~~~~~~~~~~~~~~~
.. warning::

    You may need to configure the object on the BIG-IP to get the data required
    to create the ``Resource`` classes.

Again we need to get the JSON for the object by using the CURL command.  As
we can see from the previous section's JSON output there are a few internal
data groups on the system we are testing against.  These are the items in the
``items`` list in the JSON.  We will use one of those as our example.

Looking at the ``items`` list we found that there is an internal data group
with the following ``selfLink``:
``https://localhost/mgmt/tm/ltm/data-group/internal/~Common~private_net?ver=11.6.0``

We use that URI and substitute localhost for our hostname/IP address in a
curl command.

.. code:: shell

    $> curl -k -u admin:admin https://host-vm-15/mgmt/tm/ltm/data-group/internal/~Common~private_net?ver=11.6.0
    {"kind":"tm:ltm:data-group:internal:internalstate","name":"private_net","partition":"Common","fullPath":"/Common/private_net","generation":1,"selfLink":"https://localhost/mgmt/tm/ltm/data-group/internal/~Common~private_net?ver=11.6.0","type":"ip","records":[{"name":"10.0.0.0/8"},{"name":"172.16.0.0/12"},{"name":"192.168.0.0/16"}]}

We can see that the internal data-group that is at that URI has a kind
that ends in internalstate so we know it is a ``Resource`` object.  We also
know by looking at this JSON that it does not have any sub-collections because
it does not have an ``items`` or ``reference`` attributes so this is a terminal
``Resource``.

Creating the Resource Object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
We create the resource object in the same file as the ``Collection`` object.
The code is pretty straight foward and the object inherits from
:class:`f5.bigip.resource.Resource`.  Make sure that you add the import
statement to the top of the file.

.. code:: python

    from f5.bigip.resource import Resource

    class Internal(Resource):
        """BIG-IP LTM Data Group Internal resource"""
        def __init__(self, internals):
            super(Internal, self).__init__(internals)
            self._meta_data['required_json_kind'] = \
                'tm:ltm:data-group:internal:internalstate'

Just like the previous section we need to pass into the class the container
that this resource is under.  In this case it is the ``Internals`` collection
object.  We can see this both with the URI we used to get the JSON as well
as the kind returned to us.

We also indicate the kind that this must be and this is validated by the SDK
on create and other methods to ensure that the thing we are getting back from
the BIG-IP is what we expect.

We do the same thing for the external data-group Resource.

.. code:: python

    class External(Resource):
        """BIG-IP LTM Data Group External resource"""
        def __init__(self, externals):
            super(External, self).__init__(externals)
            self._meta_data['required_json_kind'] = \
                'tm:ltm:data-group:external:externalstate'

Add the Resources to the Containers' _meta_data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Once our resources are defined we can add them to their respective containers'
``_meta_data['allowed_lazy_attributes']`` and
``_meta_data['attribute_registry']``.  The code for the Sub-collections we
created in the previous section should now look like this.

.. code:: python

    class Externals(Collection):
        """BIG-IP LTM Data Group external collection"""
        def __init__(self, data_groups):
            super(data_groups, self).__init__(data_groups)
            self._meta_data['allowed_lazy_attributes'] = [External]
            self._meta_data['attribute_registry'] = {
                'tm:ltm:data-group:external:externalstate': External
            }


    class Internals(Collection):
        """BIG-IP LTM Data Group internal collection"""
        def __init__(self, data_groups):
            super(data_groups, self).__init__(data_groups)
            self._meta_data['allowed_lazy_attributes'] = [Internal]
            self._meta_data['attribute_registry'] = {
                'tm:ltm:data-group:internal:internalstate': Internal
            }

Updating the Resources' ``_meta_data``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Overriding the Base Class's Methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Simple Test
~~~~~~~~~~~

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
    from f5.bigip.resource import Resource


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
            self._meta_data['allowed_lazy_attributes'] = [External]
            self._meta_data['attribute_registry'] = {
                'tm:ltm:data-group:external:externalstate': External
            }


    class Internals(Collection):
        """BIG-IP LTM Data Group internal collection"""
        def __init__(self, data_groups):
            super(data_groups, self).__init__(data_groups)
            self._meta_data['allowed_lazy_attributes'] = [Internal]
            self._meta_data['attribute_registry'] = {
                'tm:ltm:data-group:internal:internalstate': Internal
            }


    class Internal(Resource):
        """BIG-IP LTM Data Group Internal resource"""
        def __init__(self, internals):
            super(Internal, self).__init__(internals)
            self._meta_data['required_json_kind'] = \
                'tm:ltm:data-group:internal:internalstate'


    class External(Resource):
        """BIG-IP LTM Data Group External resource"""
        def __init__(self, externals):
            super(External, self).__init__(externals)
            self._meta_data['required_json_kind'] = \
                'tm:ltm:data-group:external:externalstate'

