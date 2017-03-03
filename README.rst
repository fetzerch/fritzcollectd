.. image:: https://circleci.com/gh/fetzerch/fritzcollectd.svg?style=shield
    :target: https://circleci.com/gh/fetzerch/fritzcollectd
    :alt: Circle CI Status

fritzcollectd
=============

A `collectd <http://collectd.org>`__ plugin for monitoring AVM FRITZ!Box
routers.

Data captured includes:

* Physical link status
* Connection status
* Online connection uptime
* Maximal bit rates
* Current bit rates
* Total bytes sent and received

Dependencies
------------
* Python 2.7+
* `fritzconnection <https://bitbucket.org/kbr/fritzconnection>`__
* `collectd <http://collectd.org>`__ 4.9+

Installation
------------
1. ``pip install fritzcollectd``
2. Configure the plugin as shown below
3. Restart collectd

Prerequisites
-------------

In order to be able to read the status information the option "Transmit status
information over UPnP" has to be enabled in the "Network Settings" menu on the
Fritz!BOX. This is exaplained in `AVM's Knowledge Base
<https://en.avm.de/service/fritzbox/fritzbox-7490/knowledge-base/publication/show/894_Setting-up-automatic-port-sharing-via-UPnP/>`_.

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
        #</Module>
    </Plugin>

The plugin recognizes several (optional) configuration parameters. In most
cases the plugin works without any of these parameters. It might be necessary
to specify `Address` if the router's host name has been changed.

* Address: The network address of the FRITZ!Box.
* Port: The TCP port of the FRITZ!Box.
* User: The login user name on the FRITZ!Box.
* Password: The password on the FRITZ!Box for authentication.
* Instance: Plugin instance that collectd associates with the data.
* Hostname: Hostname that collectd associates with the data (defaults to the
  host executing this plugin)

The module block can be repeated to monitor multiple routers.

Further Information
-------------------

Please refer to the `project announcement blog post <https://fetzerch.github.io/2014/08/23/fritzcollectd/>`__
for additional information, such as the usage of `Grafana <http://grafana.org>`__
for metrics visualization.

License
-------
This projected is licensed under the terms of the MIT license.
