# Copyright 2015 F5 Networks Inc.
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
from f5.bigip.cm.cluster import Cluster
from f5.bigip.cm import CM
from f5.bigip.cm.device import Device
from mock import MagicMock

import pytest


@pytest.fixture
def cm():
    bigip = MagicMock()
    cm = CM(bigip)
    return cm


def test_cm_init(cm):
    assert isinstance(cm.interfaces, dict)
    assert not cm.interfaces


def test_cm_uri():
    from f5.bigip.cm import base_uri
    assert base_uri == 'cm/'


def test_cm_cluster(cm):
    # This is going to throw an exception because we don't have a real BigIP
    cm.cluster.delete = MagicMock()
    cm.cluster.delete()
    assert isinstance(cm.cluster, Cluster)
    assert 'cluster' in cm.interfaces


def test_cm_device(cm):
    # This is going to throw an exception because we don't have a real BigIP
    cm.device.get_device_name = MagicMock()
    cm.device.get_device_name()
    assert isinstance(cm.device, Device)
    assert 'device' in cm.interfaces
