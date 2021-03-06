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
from f5.bigip import rest_collection
from f5.bigip.rest_collection import RESTInterfaceCollection
from f5.bigip.test.big_ip_mock import BigIPMock
from mock import call
from mock import MagicMock
from mock import Mock
from requests.exceptions import HTTPError

import os
import pytest

DATA_DIR = os.path.dirname(os.path.realpath(__file__))


class TestChild(RESTInterfaceCollection):
    def __init__(self, bigip):
        self.bigip = bigip
        self.base_uri = self.bigip.icr_url + 'root/rest'


@pytest.fixture
def RIC():
    ric = TestChild(MagicMock())
    return ric


@pytest.fixture
def LOG():
    rest_collection.Log = MagicMock()


class TestRESTInterfaceCollectionChild(RESTInterfaceCollection):
    def __init__(self, bigip):
        self.bigip = bigip
        self.base_uri = self.bigip.icr_uri + 'root/rest'


def test_exists():
    """exists() should return true for non-http error codes """
    response = BigIPMock.create_mock_response(
        200,
        BigIPMock.read_json_file(os.path.join(DATA_DIR, 'interfaces.json')))

    big_ip = BigIPMock(response)
    test_REST_iface_collection =\
        TestRESTInterfaceCollectionChild(big_ip)
    assert test_REST_iface_collection.exists()


def test_exists_404():
    """exists() should return false only for the 404 http error code """
    response = BigIPMock.create_mock_response(
        404,
        BigIPMock.read_json_file(os.path.join(DATA_DIR, 'interfaces.json')))

    big_ip = BigIPMock(response)
    big_ip.icr_session.get = Mock()
    big_ip.icr_session.get.side_effect = HTTPError(response=response)
    test_REST_iface_collection =\
        TestRESTInterfaceCollectionChild(big_ip)
    assert not test_REST_iface_collection.exists()


def test_exists_http_error():
    """exists() should raise for all other http errors """
    response = BigIPMock.create_mock_response(
        409,
        BigIPMock.read_json_file(os.path.join(DATA_DIR, 'interfaces.json')))

    big_ip = BigIPMock(response)
    big_ip.icr_session.get = Mock()
    big_ip.icr_session.get.side_effect = HTTPError(response=response)
    test_REST_iface_collection =\
        TestRESTInterfaceCollectionChild(big_ip)

    # Expect an exception because 409 is not an expected status code
    with pytest.raises(HTTPError):
        test_REST_iface_collection.exists()


def test_get_items():
    response = BigIPMock.create_mock_response(
        200,
        BigIPMock.read_json_file(os.path.join(DATA_DIR, 'interfaces.json')))

    big_ip = BigIPMock(response)
    test_REST_iface_collection =\
        TestRESTInterfaceCollectionChild(big_ip)
    names = test_REST_iface_collection._get_items()

    assert isinstance(names, list)
    assert len(names) == 10
    for i in range(1, 6):
        assert 'nat%s' % i in names


def test_get_items_invalid_select():
    response = BigIPMock.create_mock_response(
        200,
        BigIPMock.read_json_file(os.path.join(DATA_DIR, 'interfaces.json')))

    big_ip = BigIPMock(response)
    test_REST_iface_collection =\
        TestRESTInterfaceCollectionChild(big_ip)
    names = test_REST_iface_collection._get_items(select='bogus')

    assert isinstance(names, list)
    assert len(names) == 5


def test_get_items_404():
    response = BigIPMock.create_mock_response(
        404,
        BigIPMock.read_json_file(os.path.join(DATA_DIR, 'interfaces.json')))

    big_ip = BigIPMock(response)
    big_ip.icr_session.get = Mock()
    big_ip.icr_session.get.side_effect = HTTPError(response=response)
    test_REST_iface_collection =\
        TestRESTInterfaceCollectionChild(big_ip)

    # Should not raise because 404 is just not found so empty list
    names = test_REST_iface_collection._get_items()
    assert isinstance(names, list)
    assert len(names) == 0


def test_get_items_http_error():
    response = BigIPMock.create_mock_response(
        409,
        BigIPMock.read_json_file(os.path.join(DATA_DIR, 'interfaces.json')))

    big_ip = BigIPMock(response)
    big_ip.icr_session.get = Mock()
    big_ip.icr_session.get.side_effect = HTTPError(response=response)
    test_REST_iface_collection =\
        TestRESTInterfaceCollectionChild(big_ip)

    # Expect an exception because 409 is not an expected status code
    with pytest.raises(HTTPError):
        test_REST_iface_collection._get_items()


def test_get_items_uri_override():
    response = BigIPMock.create_mock_response(
        200,
        BigIPMock.read_json_file(os.path.join(DATA_DIR, 'interfaces.json')))

    big_ip = BigIPMock(response)
    test_REST_iface_collection =\
        TestRESTInterfaceCollectionChild(big_ip)
    names = test_REST_iface_collection._get_items(uri="an/overriden/uri")

    assert len(names) == 10


def test_get_items_no_items():
    response = BigIPMock.create_mock_response(
        200,
        '{"not_items": [{"a": 1}, {"b": 1}]}')

    big_ip = BigIPMock(response)
    test_REST_iface_collection =\
        TestRESTInterfaceCollectionChild(big_ip)
    names = test_REST_iface_collection._get_items()

    assert isinstance(names, list)
    assert len(names) == 0


def test_get_named_object():
    response = BigIPMock.create_mock_response(
        200,
        '{"name": "nat1"}')

    big_ip = BigIPMock(response)
    test_REST_iface_collection =\
        TestRESTInterfaceCollectionChild(big_ip)
    name = test_REST_iface_collection._get_named_object('nat1')

    assert name == 'nat1'


def test_get_named_object_http_error():
    response = BigIPMock.create_mock_response(
        404,
        BigIPMock.read_json_file(os.path.join(DATA_DIR, 'interfaces.json')))

    # Override the default jason here for single named object
    response.json = {'name': 'nat1'}

    big_ip = BigIPMock(response)
    big_ip.icr_session.get = Mock(side_effect=HTTPError(response=response))
    test_REST_iface_collection =\
        TestRESTInterfaceCollectionChild(big_ip)
    with pytest.raises(HTTPError):
        test_REST_iface_collection._get_named_object('nat1')


def test_delete():
    response = BigIPMock.create_mock_response(
        204,
        BigIPMock.read_json_file(os.path.join(DATA_DIR, 'interfaces.json')))

    big_ip = BigIPMock(response)
    test_REST_iface_collection =\
        TestRESTInterfaceCollectionChild(big_ip)

    assert test_REST_iface_collection.delete(name='nat1')


def test_delete_no_name():
    response = BigIPMock.create_mock_response(
        204,
        BigIPMock.read_json_file(os.path.join(DATA_DIR, 'interfaces.json')))

    big_ip = BigIPMock(response)
    test_REST_iface_collection =\
        TestRESTInterfaceCollectionChild(big_ip)

    assert not test_REST_iface_collection.delete()


def test_delete_404():
    response = BigIPMock.create_mock_response(
        404,
        BigIPMock.read_json_file(os.path.join(DATA_DIR, 'interfaces.json')))

    big_ip = BigIPMock(response)
    big_ip.icr_session.delete = Mock(side_effect=HTTPError(response=response))
    test_REST_iface_collection =\
        TestRESTInterfaceCollectionChild(big_ip)

    assert test_REST_iface_collection.delete(name='nat1')


def test_delete_http_error():
    response = BigIPMock.create_mock_response(
        503,
        BigIPMock.read_json_file(os.path.join(DATA_DIR, 'interfaces.json')))

    big_ip = BigIPMock(response)
    big_ip.icr_session.delete = Mock(side_effect=HTTPError(response=response))
    test_REST_iface_collection =\
        TestRESTInterfaceCollectionChild(big_ip)

    with pytest.raises(HTTPError):
        test_REST_iface_collection.delete(name='nat1')


def test_delete_all():
    response = BigIPMock.create_mock_response(
        200,
        BigIPMock.read_json_file(os.path.join(DATA_DIR, 'interfaces.json')))

    big_ip = BigIPMock(response)
    test_REST_iface_collection =\
        TestRESTInterfaceCollectionChild(big_ip)

    assert test_REST_iface_collection.delete_all()


def test_delete_all_startswith():
    response = BigIPMock.create_mock_response(
        200,
        BigIPMock.read_json_file(os.path.join(DATA_DIR, 'interfaces.json')))

    big_ip = BigIPMock(response)
    test_REST_iface_collection =\
        TestRESTInterfaceCollectionChild(big_ip)

    assert test_REST_iface_collection.delete_all(startswith="nat")


def test_delete_all_fail():
    response = BigIPMock.create_mock_response(
        200,
        BigIPMock.read_json_file(os.path.join(DATA_DIR, 'interfaces.json')))

    big_ip = BigIPMock(response)
    test_REST_iface_collection =\
        TestRESTInterfaceCollectionChild(big_ip)
    test_REST_iface_collection.delete = Mock(return_value=False)

    assert not test_REST_iface_collection.delete_all()


def test_delete_all_http_error():
    response = BigIPMock.create_mock_response(
        503,
        BigIPMock.read_json_file(os.path.join(DATA_DIR, 'interfaces.json')))

    big_ip = BigIPMock(response)
    big_ip.icr_session.delete = Mock(side_effect=HTTPError(response=response))
    test_REST_iface_collection =\
        TestRESTInterfaceCollectionChild(big_ip)

    with pytest.raises(HTTPError):
        test_REST_iface_collection.delete_all()


def test__set(RIC):
    response = RIC._set('myname', 'myfolder', 'd', 'c')
    assert RIC.bigip.icr_session.put.call_args == call(
        RIC.base_uri, folder='myfolder',
        instance_name='myname', json={'d': 'c'}, timeout=30)
    assert response


def test__set_http_error(RIC, raise_custom_HTTPError, LOG):
    RIC.bigip.icr_session.put.side_effect =\
        raise_custom_HTTPError(404, 'some text')

    with pytest.raises(HTTPError) as err_info:
        RIC._set('myname', 'myfolder', 'd', 'c')

    assert err_info.value.response.status_code == 404
    assert rest_collection.Log.error.call_args == call(
        RIC.__class__.__name__, 'some text')
