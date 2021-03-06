"""Manage application services on BIG-IP using REST interface """
# Copyright 2014-2016 F5 Networks Inc.
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

from f5.bigip.resource import Collection
from f5.bigip.resource import KindTypeMismatch
from f5.bigip.resource import Resource

from requests import HTTPError


class ApplicationCollection(Collection):
    def __init__(self, sys):
        super(ApplicationCollection, self).__init__(sys)
        self._meta_data['allowed_lazy_attributes'] = [
            APLScriptCollection,
            CustomStatCollection,
            ServiceCollection,
            TemplateCollection
        ]


class APLScriptCollection(Collection):
    def __init__(self, application):
        super(APLScriptCollection, self).__init__(application)
        self._meta_data['allowed_lazy_attributes'] = [APLScript]
        self._meta_data['attribute_registry'] =\
            {'tm:sys:application:apl-script:apl-scriptstate': APLScript}


class APLScript(Resource):
    def __init__(self, apl_script_collection):
        super(APLScript, self).__init__(apl_script_collection)
        self._meta_data['required_json_kind'] =\
            'tm:sys:application:apl-script:apl-scriptstate'


class CustomStatCollection(Collection):
    def __init__(self, application):
        super(CustomStatCollection, self).__init__(application)
        self._meta_data['allowed_lazy_attributes'] = [CustomStat]
        self._meta_data['attribute_registry'] =\
            {'tm:sys:application:custom-stat:custom-statstate': CustomStat}


class CustomStat(Resource):
    def __init__(self, custom_stat_collection):
        super(CustomStat, self).__init__(custom_stat_collection)
        self._meta_data['required_json_kind'] =\
            'tm:sys:application:custom-stat:custom-statstate'


class ServiceCollection(Collection):
    def __init__(self, application):
        super(ServiceCollection, self).__init__(application)
        self._meta_data['allowed_lazy_attributes'] = [Service]
        self._meta_data['attribute_registry'] =\
            {'tm:sys:application:service:servicestate': Service}


class Service(Resource):
    def __init__(self, service_collection):
        super(Service, self).__init__(service_collection)
        self._meta_data['required_creation_parameters'].update(('template',))
        self._meta_data['required_refresh_parameters'].update(('partition',))
        self._meta_data['required_json_kind'] =\
            'tm:sys:application:service:servicestate'

    def _create(self, **kwargs):
        '''Create service on device and create accompanying Python object.

        :params kwargs: keyword arguments passed in from create call
        :raises: KindTypeMismatch
        :raises: HTTPError
        :returns: Python Service object
        '''

        try:
            super(Service, self)._create(**kwargs)
        except HTTPError as ex:
            if "The configuration was updated successfully but could not be " \
                    "retrieved" not in ex.response.text:
                raise

            # BigIP will create in Common partition if none is given.
            # In order to create the uri properly in this class's load,
            # drop in Common as the partition in kwargs.
            if 'partition' not in kwargs:
                kwargs['partition'] = 'Common'
            # 'template' kwarg should not be used in the call to load becuase
            # the BigIP will return an error if it's present
            kwargs.pop('template')

            # If response was created successfully, do a local_update.
            # If not, call to overridden _load method via load
            self.load(**kwargs)
            if self.kind != self._meta_data['required_json_kind']:
                error_message = "For instances of type '%r' the corresponding"\
                    " kind must be '%r' but creation returned JSON with kind: %r"\
                    % (self.__class__.__name__,
                       self._meta_data['required_json_kind'],
                       self.kind)
                raise KindTypeMismatch(error_message)

        return self

    def update(self, **kwargs):
        '''Push local updates to the object on the device.

        :params kwargs: keyword arguments for accessing/modifying the object
        :returns: updated Python object
        '''

        inherit_device_group = self.__dict__.get('inheritedDevicegroup', False)
        if inherit_device_group == 'true':
            self.__dict__.pop('deviceGroup')
        return self._update(**kwargs)

    def _load(self, **kwargs):
        '''Load python Service object with response JSON from BigIP.

        :params kwargs: keyword arguments for talking to the device
        :returns: populated Service object
        '''

        self._check_load_parameters(**kwargs)
        name = kwargs.pop('name')
        partition = kwargs.pop('partition')
        read_session = self._meta_data['bigip']._meta_data['icr_session']
        base_uri = self._meta_data['container']._meta_data['uri']

        name = name.replace('/', '~')
        load_uri = '%s~%s~%s.app~%s' % (base_uri, partition, name, name)

        response = read_session.get(load_uri, uri_as_parts=False, **kwargs)
        self._local_update(response.json())
        self._build_meta_data_uri(self.selfLink)
        return self


class TemplateCollection(Collection):
    def __init__(self, application):
        super(TemplateCollection, self).__init__(application)
        self._meta_data['allowed_lazy_attributes'] = [Template]
        self._meta_data['attribute_registry'] =\
            {'tm:sys:application:template:templatestate': Template}


class Template(Resource):
    def __init__(self, template_collection):
        super(Template, self).__init__(template_collection)
        self._meta_data['required_json_kind'] =\
            'tm:sys:application:template:templatestate'
