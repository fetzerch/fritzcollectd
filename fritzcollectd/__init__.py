# fritzcollectd - FRITZ!Box collectd plugin
# Copyright (c) 2014-2019 Christian Fetzer
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

# pylint: disable=bad-option-value,useless-object-inheritance

""" fritzcollectd - FRITZ!Box collectd plugin """

from collections import namedtuple, OrderedDict

import fritzconnection
import pbr.version

from lxml.etree import XMLSyntaxError  # pylint: disable=no-name-in-module

import collectd  # pylint: disable=import-error

__version__ = pbr.version.VersionInfo('fritzcollectd').release_string()


CONFIGS = []


class FritzCollectd(object):
    """ Collect data from FRITZ!Box and dispatch them to collectd """

    # pylint: disable=too-many-instance-attributes

    PLUGIN_NAME = 'fritzbox'

    ServiceAction = namedtuple(
        'ServiceAction', ['service', 'action',
                          'index_field', 'instance_field', 'instance_prefix'])
    ServiceAction.__new__.__defaults__ = (None, None, None)
    Value = namedtuple('ServiceValue', ['value_instance', 'value_type'])

    # Services/Actions/Arguments that are read from the router.
    # dict: {(service, service_action):
    #           {action_argument: (value_instance, value_type)}}
    SERVICE_ACTIONS = OrderedDict([
        (ServiceAction('WANIPConn:1', 'GetStatusInfo'),
         {'NewConnectionStatus': Value('constatus', 'gauge'),
          'NewUptime': Value('uptime', 'uptime')}),
        (ServiceAction('WANCommonIFC:1', 'GetCommonLinkProperties'),
         {'NewPhysicalLinkStatus': Value('dslstatus', 'gauge'),
          'NewLayer1DownstreamMaxBitRate': Value('downstreammax', 'bitrate'),
          'NewLayer1UpstreamMaxBitRate': Value('upstreammax', 'bitrate')}),
        (ServiceAction('WANCommonIFC:1', 'GetAddonInfos'),
         {'NewByteSendRate': Value('sendrate', 'bitrate'),
          'NewByteReceiveRate': Value('receiverate', 'bitrate'),
          'NewTotalBytesSent': Value('totalbytessent', 'bytes'),
          'NewTotalBytesReceived': Value('totalbytesreceived', 'bytes')}),
        (ServiceAction('DeviceInfo:1', 'GetInfo'),
         {'NewUpTime': Value('boxuptime', 'uptime')}),
        (ServiceAction('LANEthernetInterfaceConfig:1', 'GetStatistics'),
         {'NewBytesSent': Value('lan_totalbytessent', 'bytes'),
          'NewBytesReceived': Value('lan_totalbytesreceived', 'bytes')}),
        (ServiceAction('WANCommonInterfaceConfig:1',
                       'GetCommonLinkProperties'),
         {'NewLayer1DownstreamMaxBitRate':
          Value('linkdownstreammax', 'bitrate'),
          'NewLayer1UpstreamMaxBitRate': Value('linkupstreammax', 'bitrate')}),
        (ServiceAction('X_AVM-DE_Homeauto:1', 'GetGenericDeviceInfos',
                       'NewIndex', 'NewIndex', 'dect'),
         {'NewMultimeterPower': Value('power', 'power'),
          'NewMultimeterEnergy': Value('energy', 'power'),
          'NewTemperatureCelsius': Value('temperature', 'temperature'),
          'NewSwitchState': Value('switchstate', 'gauge')}),
    ])

    CONVERSION = {
        'NewPhysicalLinkStatus': lambda x: 1 if x == 'Up' else 0,
        'NewConnectionStatus': lambda x: 1 if x == 'Connected' else 0,
        'NewByteSendRate': lambda x: 8 * x,
        'NewByteReceiveRate': lambda x: 8 * x,
        'NewTemperatureCelsius': lambda x: float(x) / 10,
        'NewSwitchState': lambda x: 1 if x == 'ON' else 0,
        'NewMultimeterEnergy': lambda x: float(x) / 1000,
        'NewMultimeterPower': lambda x: float(x) / 100
    }

    def __init__(self,  # pylint: disable=too-many-arguments
                 address=fritzconnection.fritzconnection.FRITZ_IP_ADDRESS,
                 port=fritzconnection.fritzconnection.FRITZ_TCP_PORT,
                 user=fritzconnection.fritzconnection.FRITZ_USERNAME,
                 password='',
                 hostname='',
                 plugin_instance='',
                 verbose=''):
        self._fritz_address = address
        self._fritz_port = port
        self._fritz_user = user
        self._fritz_password = password
        self._fritz_hostname = hostname
        self._plugin_instance = plugin_instance
        self._verbose = verbose.lower() in ['true', 'yes']
        if self._verbose:
            collectd.info("fritzcollectd: Verbose logging enabled")
        self._fc = None

    def _dispatch_value(self, plugin_instance,
                        value_type, value_instance, value):
        """ Dispatch value to collectd """
        val = collectd.Values()
        val.host = self._fritz_hostname
        val.plugin = self.PLUGIN_NAME
        val.plugin_instance = plugin_instance
        val.type = value_type
        val.type_instance = value_instance
        val.values = [value]
        if self._verbose:
            collectd.info("fritzcollectd: Dispatching: host: '{}', "
                          "plugin: '{}', plugin_instance: '{}', type: '{}', "
                          "type_instance: '{}', values: '{}'".format(
                              val.host, val.plugin, val.plugin_instance,
                              val.type, val.type_instance, val.values))
        val.dispatch()

    def init(self):
        """ Initialize the connection to the FRITZ!Box """
        self._fc = fritzconnection.FritzConnection(
            address=self._fritz_address, port=self._fritz_port,
            user=self._fritz_user, password=self._fritz_password)
        if self._fc.modelname is None:
            self._fc = None
            raise IOError("fritzcollectd: Failed to connect to %s" %
                          self._fritz_address)

        if not self._fc.call_action('WANIPConn:1', 'GetStatusInfo'):
            self._fc = None
            raise IOError("fritzcollectd: Statusinformation via UPnP is "
                          "not enabled")

        if self._fritz_password != '':
            # If the 'Allow access for applications' option is disabled,
            # the connection behaves as if it was created without password.
            if 'WANIPConnection:1' not in self._fc.services.keys():
                self._fc = None
                raise IOError("fritzcollectd: Allow access for applications "
                              "is not enabled")

            try:
                self._fc.call_action('WANIPConnection:1', 'GetStatusInfo')
            except fritzconnection.AuthorizationError:
                self._fc = None
                raise IOError("fritzcollectd: Incorrect password or "
                              "'FRITZ!Box Settings' rights for user disabled")
        else:
            collectd.info("fritzcollectd: No password configured, "
                          "some values cannot be queried")

        self._filter_service_actions(self.SERVICE_ACTIONS,
                                     self._fc.actionnames)

    @classmethod
    def _filter_service_actions(cls, service_actions, actionnames):
        """ Remove unsupported service actions """
        for service_action in list(service_actions.keys()):
            if ((service_action.service, service_action.action)
                    not in actionnames):
                collectd.info("fritzcollectd: Skipping unsupported service "
                              "action: {} {}".format(service_action.service,
                                                     service_action.action))
                del service_actions[service_action]

    def read(self):
        """ Read and dispatch """
        values = self._read_data(self.SERVICE_ACTIONS, self._fc)
        for (instance, value_instance), (value_type, value) in values.items():
            self._dispatch_value(instance, value_type, value_instance, value)

    def _read_data(self, service_actions, connection):
        """ Read data from the FRITZ!Box

            The data is read from all services & actions defined in
            SERVICE_ACTIONS.
            This function returns a dict in the following format:
            {value_instance: (value_type, value)}
        """

        # Don't try to gather data if the connection is not available
        if connection is None:
            return {}

        # Construct a dict:
        # {(plugin_instance, value_instance): (value_type, value)} from the
        # queried results and applies a value conversion (if defined)
        values = {}
        for service_action in service_actions:
            index = 0
            while True:
                parameters = {service_action.index_field: index} \
                             if service_action.index_field else {}
                if self._verbose:
                    collectd.info("fritzcollectd: Calling action: "
                                  "{} {} {}".format(service_action.service,
                                                    service_action.action,
                                                    parameters))
                readings = connection.call_action(
                    service_action.service, service_action.action,
                    **parameters)
                if not readings:
                    if self._verbose:
                        collectd.info("fritzcollectd: No readings received")
                    break

                plugin_instance = [self._plugin_instance]
                if service_action.instance_field:
                    readings.update(parameters)
                    plugin_instance.append('{}{}'.format(
                        service_action.instance_prefix,
                        readings[service_action.instance_field]
                    ))
                plugin_instance = '-'.join(filter(None, plugin_instance))

                values.update({  # pragma: no branch
                    (plugin_instance, value.value_instance): (
                        value.value_type,
                        self.CONVERSION.get(action_argument, lambda x: x)(
                            readings[action_argument])
                    )
                    for (action_argument, value)
                    in service_actions[service_action].items()
                })

                if not service_action.index_field:
                    break
                index += 1

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
        elif node.key == 'Verbose':
            params['verbose'] = node.values[0]
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
        try:
            config.read()
        except XMLSyntaxError:
            collectd.warning('fritzcollectd: Invalid data received, '
                             'attempting to reconnect')
            config.init()


def callback_shutdown():
    """ Shutdown callback """
    del CONFIGS[:]


collectd.register_config(callback_configure)
collectd.register_init(callback_init)
collectd.register_read(callback_read)
collectd.register_shutdown(callback_shutdown)
