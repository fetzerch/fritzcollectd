# fritzcollectd - FRITZ!Box collectd plugin
# Copyright (c) 2014-2016 Christian Fetzer
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

import collectd  # pylint: disable=import-error
import fritzconnection

__version__ = '0.2.1'


class FritzCollectd(object):
    """ Collect data from FRITZ!Box and dispatch them to collectd """

    # pylint: disable=too-many-instance-attributes

    PLUGIN_NAME = 'fritzbox'

    SERVICE_ACTIONS = [
        ('WANIPConnection', 'GetStatusInfo'),
        ('WANCommonInterfaceConfig', 'GetCommonLinkProperties'),
        ('WANCommonInterfaceConfig', 'GetAddonInfos')
    ]

    VALUES = {
        'NewPhysicalLinkStatus': ('dslstatus', 'gauge'),
        'NewConnectionStatus': ('constatus', 'gauge'),
        'NewUptime': ('uptime', 'uptime'),
        'NewLayer1DownstreamMaxBitRate': ('downstreammax', 'bitrate'),
        'NewLayer1UpstreamMaxBitRate': ('upstreammax', 'bitrate'),
        'NewByteSendRate': ('sendrate', 'bitrate'),
        'NewByteReceiveRate': ('receiverate', 'bitrate'),
        'NewTotalBytesSent': ('totalbytessent', 'bytes'),
        'NewTotalBytesReceived': ('totalbytesreceived', 'bytes')
    }

    CONVERSION = {
        'NewPhysicalLinkStatus': lambda x: 1 if x == 'Up' else 0,
        'NewConnectionStatus': lambda x: 1 if x == 'Connected' else 0,
        'NewByteSendRate': lambda x: 8 * x,
        'NewByteReceiveRate': lambda x: 8 * x
    }

    def __init__(self):
        self._fritz_address = fritzconnection.fritzconnection.FRITZ_IP_ADDRESS
        self._fritz_port = fritzconnection.fritzconnection.FRITZ_TCP_PORT
        self._fritz_user = fritzconnection.fritzconnection.FRITZ_USERNAME
        self._fritz_password = ''
        self._fritz_hostname = ''
        self._plugin_instance = ''
        self._verbose = False
        self._fc = None

    def callback_configure(self, config):
        """ Configure callback """
        for node in config.children:
            if node.key == 'Address':
                self._fritz_address = node.values[0]
            elif node.key == 'Port':
                self._fritz_port = int(node.values[0])
            elif node.key == 'User':
                self._fritz_user = node.values[0]
            elif node.key == 'Password':
                self._fritz_password = node.values[0]
            elif node.key == 'Hostname':
                self._fritz_hostname = node.values[0]
            elif node.key == 'Instance':
                self._plugin_instance = node.values[0]
            else:
                collectd.warning('fritzcollectd: Unknown config %s' % node.key)

    def callback_init(self):
        """ Init callback

            Initialize the connection to the FRITZ!Box
        """
        self.fritz_init()

    def callback_read(self):
        """ Read callback

            Read data from the FRITZ!Box and dispatch values to collectd.
        """
        values = self.fritz_read_data()
        for instance, (value_type, value) in values.items():
            self._dispatch_value(value_type, instance, value)

    def _dispatch_value(self, value_type, instance, value):
        """ Dispatch value to collectd """
        val = collectd.Values()
        val.host = self._fritz_hostname
        val.plugin = self.PLUGIN_NAME
        val.plugin_instance = self._plugin_instance
        val.type = value_type
        val.type_instance = instance
        val.values = [value]
        val.dispatch()

    def fritz_init(self):
        """ Initialize the connection to the FRITZ!Box """
        try:
            self._fc = fritzconnection.FritzConnection(
                address=self._fritz_address, port=self._fritz_port,
                user=self._fritz_user, password=self._fritz_password)
        except IOError:
            collectd.error("fritzcollectd: Failed to connect to %s" %
                           self._fritz_address)

    def fritz_read_data(self):
        """ Read data from the FRITZ!Box

            The data is read from all actions defined in SERVICE_ACTIONS.
            This function returns a dict in the following format:
            {instance: (value_type, value)} where value_type and instance are
            mapped from VALUES and CONVERSION.
        """
        values = {}

        # Don't try to gather data if the connection is not available
        if self._fc is None:
            return values

        # Combine all values available in SERVICE_ACTIONS into a dict
        for service, action in self.SERVICE_ACTIONS:
            values.update(self._fc.call_action(service, action))

        # Construct a dict: {instance: (value_type, value)} from the queried
        # results applying a conversion (if defined)
        result = {
            instance:
            (value_type,
             self.CONVERSION.get(key, lambda x: x)(values.get(key)))
            for key, (instance, value_type) in self.VALUES.items()
        }
        return result


FC = FritzCollectd()
collectd.register_config(FC.callback_configure)
collectd.register_init(FC.callback_init)
collectd.register_read(FC.callback_read)
