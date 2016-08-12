fritzcollectd
=============

A `collectd <http://collectd.org>`_ plugin for monitoring AVM FRITZ!Box
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
* `fritzconnection <https://bitbucket.org/kbr/fritzconnection>`_
* `collectd <http://collectd.org>`_ 4.9+

Installation
------------
1. ``pip install fritzcollectd``
2. Configure the plugin as shown below
3. Restart collectd

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
        #    Hostname "FritzBox"
        #    Password "pass"
        #    Instance "1"
        #</Module>
    </Plugin>

The plugin recognizes several (optional) configuration parameters.

* Address: The address of the FRITZ!Box
* Port: The port of the FRITZ!Box
* User: Login user name
* Password: Password for authentication
* Instance: collectd plugin instance
* Hostname: Hostname that collectd associates with the data (defaults to the
  host executing this plugin)

License
-------
This projected is licensed under the terms of the MIT license.
