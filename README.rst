.. image:: https://travis-ci.org/fetzerch/fritzcollectd.svg?branch=master
    :target: https://travis-ci.org/fetzerch/fritzcollectd
    :alt: Travis CI Status

.. image:: https://coveralls.io/repos/github/fetzerch/fritzcollectd/badge.svg?branch=master
    :target: https://coveralls.io/github/fetzerch/fritzcollectd?branch=master
    :alt: Coveralls Status

.. image:: https://img.shields.io/pypi/v/fritzcollectd.svg
    :target: https://pypi.org/project/fritzcollectd
    :alt: PyPI Version

fritzcollectd
=============

A `collectd <http://collectd.org>`__ plugin for monitoring AVM FRITZ!Box
routers.

Data captured for the FRITZ!Box includes:

* Physical link status
* Connection status
* Online connection uptime
* Maximal bit rates
* Current bit rates
* Total bytes sent and received
* Total bytes send and received on LAN interface (requires authentication)
* Router uptime (requires authentication)

Data captured for connected FRITZ!DECT devices (requires authentication):

* Temperature
* Switch status
* Current power
* Energy consumption

Dependencies
------------
* Python 2.7+
* `fritzconnection <https://github.com/kbr/fritzconnection>`__
* `collectd <http://collectd.org>`__ 4.9+

Installation
------------
1. ``pip install fritzcollectd``
2. Configure the plugin as shown below
3. Restart collectd

Prerequisites
-------------

In order to be able to read the status information the option `"Transmit status
information over UPnP" <https://en.avm.de/service/fritzbox/fritzbox-7490/knowledge-base/publication/show/894_Setting-up-automatic-port-sharing-via-UPnP/>`_
has to be enabled in the "Network Settings" menu on the Fritz!BOX.

For reading values that are marked with *requires authentication* in the
introduction section, the option "Allow access for applications" (also in
"Network Settings") has to be enabled as well. If desired a separate user
account can be created for gathering statistics in `"FRITZ!Box Users" in the
"System" menu <https://en.avm.de/service/fritzbox/fritzbox-4020/knowledge-base/publication/show/1522_Accessing-FRITZ-Box-from-the-home-network-with-user-accounts/>`_.
The account needs to have the "FRITZ!Box Settings" permission.

Configuration
-------------
Add the following to your collectd config (typically ``/etc/collectd.conf``):

.. code:: xml

    <LoadPlugin python>
        Globals true
    </LoadPlugin>
    ...
    <Plugin python>
        Import "fritzcollectd"

        #<Module fritzcollectd>
        #    Address "fritz.box"
        #    Port 49000
        #    User "dslf-config"
        #    Password "pass"
        #    Hostname "FritzBox"
        #    Instance "1"
        #    Verbose "False"
        #</Module>
    </Plugin>

The plugin recognizes several (optional) configuration parameters. In most
cases the plugin works without any of these parameters. It might be necessary
to specify `Address` if the router's host name has been changed. The values
in the introduction section that are marked with *requires authentication*
can only be queried if the router's `Password` has been configured (see also
the prerequisites section).

* Address: The network address of the FRITZ!Box.
* Port: The TCP port of the FRITZ!Box.
* User: The login user name on the FRITZ!Box.
* Password: The password on the FRITZ!Box for authentication.
* Instance: Plugin instance that collectd associates with the data.
* Hostname: Hostname that collectd associates with the data (defaults to the
  host executing this plugin)
* Verbose: Enable verbose logging to ease debugging.

The module block can be repeated to monitor multiple routers.

Further Information
-------------------

Please refer to the `project announcement blog post <https://fetzerch.github.io/2014/08/23/fritzcollectd/>`__
for additional information, such as the usage of `Grafana <http://grafana.org>`__
for metrics visualization.

License
-------
This projected is licensed under the terms of the MIT license.
