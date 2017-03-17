# fritzcollectd - FRITZ!Box collectd plugin
# Copyright (c) 2014-2017 Christian Fetzer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

""" fritzcollectd - FRITZ!Box collectd plugin """

from collections import namedtuple, OrderedDict

import collectd  # pylint: disable=import-error
import fritzconnection

from lxml.etree import XMLSyntaxError  # pylint: disable=no-name-in-module

__version__ = '0.4.0'


CONFIGS = []


class FritzCollectd(object):
    """ Collect data from FRITZ!Box and dispatch them to collectd """

    # pylint: disable=too-many-instance-attributes

    PLUGIN_NAME = 'fritzbox'

    ServiceAction = namedtuple('ServiceAction', ['service', 'action'])
    Value = namedtuple('ServiceValue', ['value_instance', 'value_type'])

    # Services/Actions/Arguments that are read from the router.
    # dict: {(service, service_action):
    #           {action_argument: (value_instance, value_type)}}
    SERVICE_ACTIONS = OrderedDict([
        (ServiceAction('WANIPConnection', 'GetStatusInfo'),
         {'NewConnectionStatus': Value('constatus', 'gauge'),
          'NewUptime': Value('uptime', 'uptime')}),
        (ServiceAction('WANCommonInterfaceConfig', 'GetCommonLinkProperties'),
         {'NewPhysicalLinkStatus': Value('dslstatus', 'gauge'),
          'NewLayer1DownstreamMaxBitRate': Value('downstreammax', 'bitrate'),
          'NewLayer1UpstreamMaxBitRate': Value('upstreammax', 'bitrate')}),
        (ServiceAction('WANCommonInterfaceConfig', 'GetAddonInfos'),
         {'NewByteSendRate': Value('sendrate', 'bitrate'),
          'NewByteReceiveRate': Value('receiverate', 'bitrate'),
          'NewTotalBytesSent': Value('totalbytessent', 'bytes'),
          'NewTotalBytesReceived': Value('totalbytesreceived', 'bytes')})
    ])

    # Services/Actions that require authentication with password
    SERVICE_ACTIONS_AUTH = OrderedDict([
        (ServiceAction('LANEthernetInterfaceConfig', 'GetStatistics'),
         {'NewBytesSent': Value('lan_totalbytessent', 'bytes'),
          'NewBytesReceived': Value('lan_totalbytesreceived', 'bytes')}),
    ])

    CONVERSION = {
        'NewPhysicalLinkStatus': lambda x: 1 if x == 'Up' else 0,
        'NewConnectionStatus': lambda x: 1 if x == 'Connected' else 0,
        'NewByteSendRate': lambda x: 8 * x,
        'NewByteReceiveRate': lambda x: 8 * x
    }

    def __init__(self,  # pylint: disable=too-many-arguments
                 address=fritzconnection.fritzconnection.FRITZ_IP_ADDRESS,
                 port=fritzconnection.fritzconnection.FRITZ_TCP_PORT,
                 user=fritzconnection.fritzconnection.FRITZ_USERNAME,
                 password='',
                 hostname='',
                 plugin_instance=''):
        self._fritz_address = address
        self._fritz_port = port
        self._fritz_user = user
        self._fritz_password = password
        self._fritz_hostname = hostname
        self._plugin_instance = plugin_instance
        self._fc = None
        self._fc_auth = None

    def _dispatch_value(self, value_type, value_instance, value):
        """ Dispatch value to collectd """
        val = collectd.Values()
        val.host = self._fritz_hostname
        val.plugin = self.PLUGIN_NAME
        val.plugin_instance = self._plugin_instance
        val.type = value_type
        val.type_instance = value_instance
        val.values = [value]
        val.dispatch()

    def init(self):
        """ Initialize the connection to the FRITZ!Box """
        self._fc = fritzconnection.FritzConnection(
            address=self._fritz_address, port=self._fritz_port,
            user=self._fritz_user)
        if self._fc.modelname is None:
            raise IOError("fritzcollectd: Failed to connect to %s" %
                          self._fritz_address)

        if len(self._fc.call_action('WANIPConnection',
                                    'GetStatusInfo')) == 0:
            raise IOError("fritzcollectd: Statusinformation via UPnP is "
                          "not enabled")

        if self._fritz_password != '':
            self._fc_auth = fritzconnection.FritzConnection(
                address=self._fritz_address, port=self._fritz_port,
                user=self._fritz_user, password=self._fritz_password)
            try:
                self._fc_auth.call_action('WANIPConnection',
                                          'GetStatusInfo')
            except XMLSyntaxError:
                raise IOError("fritzcollectd: Incorrect password")

    def read(self):
        """ Read and dispatch """
        values = self._read_data(self.SERVICE_ACTIONS, self._fc)
        for value_instance, (value_type, value) in values.items():
            self._dispatch_value(value_type, value_instance, value)

        values = self._read_data(self.SERVICE_ACTIONS_AUTH, self._fc_auth)
        for value_instance, (value_type, value) in values.items():
            self._dispatch_value(value_type, value_instance, value)

    @classmethod
    def _read_data(cls, service_actions, connection):
        """ Read data from the FRITZ!Box

            The data is read from all services & actions defined in
            SERVICE_ACTIONS.
            This function returns a dict in the following format:
            {value_instance: (value_type, value)}
        """

        # Don't try to gather data if the connection is not available
        if connection is None:
            return {}

        # Construct a dict: {value_instance: (value_type, value)} from the
        # queried results and applies a value conversion (if defined)
        values = {}
        for service_action in service_actions:
            readings = connection.call_action(service_action.service,
                                              service_action.action)
            values.update({
                value.value_instance: (
                    value.value_type,
                    cls.CONVERSION.get(action_argument, lambda x: x)(
                        readings[action_argument])
                )
                for (action_argument, value)
                in service_actions[service_action].items()
            })
        return values


def callback_configure(config):
    """ Configure callback """
    params = {}
    for node in config.children:
        if node.key == 'Address':
            params['address'] = node.values[0]
        elif node.key == 'Port':
            params['port'] = int(node.values[0])
        elif node.key == 'User':
            params['user'] = node.values[0]
        elif node.key == 'Password':
            params['password'] = node.values[0]
        elif node.key == 'Hostname':
            params['hostname'] = node.values[0]
        elif node.key == 'Instance':
            params['plugin_instance'] = node.values[0]
        else:
            collectd.warning('fritzcollectd: Unknown config %s' % node.key)
    CONFIGS.append(FritzCollectd(**params))


def callback_init():
    """ Init callback """
    for config in CONFIGS:
        config.init()


def callback_read():
    """ Read callback """
    for config in CONFIGS:
        config.read()


def callback_shutdown():
    """ Shutdown callback """
    del CONFIGS[:]


collectd.register_config(callback_configure)
collectd.register_init(callback_init)
collectd.register_read(callback_read)
collectd.register_shutdown(callback_shutdown)
