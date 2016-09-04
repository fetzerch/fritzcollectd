import collections
import mock
import sys

from nose.tools import raises, nottest

class FritzcollectdMock(mock.Mock):
    pass

class CollectdMock(mock.Mock):
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
    def process(cls, config):
        MOCK.cb_config(config)
        MOCK.cb_init()
        MOCK.cb_read()

    VALUES = mock.MagicMock()
    @classmethod
    def Values(cls):
        return cls.VALUES

MOCK = CollectdMock()
sys.modules['collectd'] = MOCK
from fritzcollectd import *

def test_setup():
    assert FC != None
    assert MOCK.cb_config != None
    assert MOCK.cb_init != None
    assert MOCK.cb_read != None


SAMPLE = {
    'NewByteSendRate': 747,
    'NewTotalBytesSent': 1619047395,
    'NewAutoDisconnectTime': 0,
    'NewLastConnectionError': 'ERROR_NONE',
    'NewUpnpControlEnabled': '0',
    'NewByteReceiveRate': 135,
    'NewRoutedBridgedModeBoth': 1,
    'NewLayer1UpstreamMaxBitRate': 2105000,
    'NewWANAccessType': 'DSL',
    'NewIdleDisconnectTime': 0,
    'NewVoipDNSServer2': '217.237.151.142',
    'NewDNSServer1': '217.237.150.188',
    'NewDNSServer2': '217.237.151.142',
    'NewLayer1DownstreamMaxBitRate': 10087000,
    'NewConnectionStatus': 'Connected',
    'NewVoipDNSServer1': '217.237.150.188',
    'NewUptime': 58736,
    'NewPacketReceiveRate': 0,
    'NewPhysicalLinkStatus': 'Up',
    'NewPacketSendRate': 0,
    'NewTotalBytesReceived': 4249590776
}


class Config():  # pylint: disable=too-few-public-methods
    """ Config element passed to the fritzcollectd configuration callback. """
    def __init__(self, config):
        self._config = config

    def __str__(self):
        return str(self.children)

    @property
    def children(self):
        """ Property passed to fritzcollectd's configuration callback. """
        node = collections.namedtuple('Node', ['key', 'values'])
        return [node(key=k, values=[v]) for k, v in self._config.items()]

FRITZBOX_DATA = [{
    'NewConnectionStatus': 'Connected',
    'NewLastConnectionError': 'ERROR_NONE',
    'NewUptime': 35307
}, {
    'NewWANAccessType': 'DSL',
    'NewLayer1DownstreamMaxBitRate': 10087000,
    'NewPhysicalLinkStatus': 'Up',
    'NewLayer1UpstreamMaxBitRate': 2105000
}, {
    'NewVoipDNSServer1': '192.168.0.1',
    'NewVoipDNSServer2': '192.168.0.2',
    'NewByteSendRate': 3438,
    'NewByteReceiveRate': 67649,
    'NewUpnpControlEnabled': '0',
    'NewTotalBytesSent': 1712232562,
    'NewDNSServer2': '192.168.0.3',
    'NewDNSServer1': '192.168.0.4',
    'NewIdleDisconnectTime': 2,
    'NewAutoDisconnectTime': 0,
    'NewRoutedBridgedModeBoth': 1,
    'NewTotalBytesReceived': 5221019883,
    'NewPacketReceiveRate': 0,
    'NewPacketSendRate': 0
}]

@mock.patch('fritzconnection.FritzConnection', autospec = True)
def test_basic(fc_class_mock):
    config = Config({'Address': 'localhost'})
    try:
        fc_mock = mock.Mock()
        fc_class_mock.return_value = fc_mock
        fc_mock.call_action.side_effect = FRITZBOX_DATA
        MOCK.process(config)
    finally:
        print("classfritzcalls: {}".format(fc_class_mock.mock_calls))
        print("collectd  : {}".format(MOCK.mock_calls))
        print("val  : {}".format(MOCK.Values().mock_calls))

@nottest
def test_system_connectionfailure():
    config = mock.MagicMock()
    Node = collections.namedtuple('Node', ['key', 'values'])
    config.children = [
        Node('Address', ['localhost']),
    ]
    MOCK.cb_config(config)
    MOCK.cb_init()
    MOCK.cb_read()

@nottest
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
