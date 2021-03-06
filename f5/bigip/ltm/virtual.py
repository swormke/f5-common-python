# Copyright 2014 F5 Networks Inc.
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
from f5.bigip.resource import Resource


class VirtualCollection(Collection):
    def __init__(self, ltm):
        super(VirtualCollection, self).__init__(ltm)
        self._meta_data['allowed_lazy_attributes'] = [Virtual]
        self._meta_data['attribute_registry'] =\
            {'tm:ltm:virtual:virtualstate': Virtual}


class Virtual(Resource):
    def __init__(self, virtual_collection):
        super(Virtual, self).__init__(virtual_collection)
        self._meta_data['required_json_kind'] = 'tm:ltm:virtual:virtualstate'
