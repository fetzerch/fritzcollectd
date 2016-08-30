import collections
import mock
import sys

from nose.tools import raises

class CollectdMock:
    @classmethod
    def register_config(cls, cb_config):
        cls.cb_config = cb_config

    @classmethod
    def register_init(cls, cb_init):
        cls.cb_init = cb_init

    @classmethod
    def register_read(cls, cb_read):
        cls.cb_read = cb_read

    @classmethod
    def error(cls, message):
        pass

    @classmethod
    def warning(cls, message):
        pass

    @classmethod
    def Values(cls):
        values = mock.MagicMock()
        #values.dispatch.side_effect = Exception('dis')
        return values

MOCK = CollectdMock()
sys.modules['collectd'] = MOCK
from fritzcollectd import *

def test_setup():
    assert FC != None
    assert MOCK.cb_config != None
    assert MOCK.cb_init != None
    assert MOCK.cb_read != None

def test_system_connectionfailure():
    config = mock.MagicMock()
    Node = collections.namedtuple('Node', ['key', 'values'])
    config.children = [
        Node('Address', ['localhost']),
    ]
    MOCK.cb_config(config)
    MOCK.cb_init()
    MOCK.cb_read()

def test_system_connection():
    config = mock.MagicMock()
    Node = collections.namedtuple('Node', ['key', 'values'])
    config.children = [
        Node('Address', ['fritz.box']),
        Node('Port', [49000]),
        Node('User', ['']),
        Node('Password', ['']),
        Node('Hostname', ['host']),
        Node('Instance', ['instance']),
        Node('NonExistent', ['nonexistent'])
    ]
    MOCK.cb_config(config)
    MOCK.cb_init()
    MOCK.cb_read()
