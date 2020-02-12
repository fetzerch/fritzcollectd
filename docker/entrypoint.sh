#!/bin/bash

# access to InfluxDB
INFLUXDB_HOST=${INFLUXDB_HOST:-influxdb}
INFLUXDB_PORT=${INFLUXDB_PORT:-25826}

# access to FritzBox
FRITZBOX_HOST=${FRITZBOX_HOST:-fritz.box}
FRITZBOX_PORT=${FRITZBOX_PORT:-49000}

# reported hostname
FRITZBOX_HOSTNAME=${FRITZBOX_HOSTNAME:fritzbox}

# Plugin verbosity
VERBOSE=${VERBOSE:-false}

cat > /etc/collectd/collectd.conf <<EOF
FQDNLookup true
LoadPlugin logfile

<Plugin logfile>
    LogLevel "info"
    File STDOUT
    Timestamp true
    PrintSeverity false
</Plugin>

LoadPlugin network
LoadPlugin python

<Plugin network>
    Server "$INFLUXDB_HOST" "$INFLUXDB_PORT"
</Plugin>
<Plugin python>
    Import "fritzcollectd"

    <Module fritzcollectd>
         Address "$FRITZBOX_HOST"
         Port $FRITZBOX_PORT
         User "$FRITZBOX_USER"
         Password "$FRITZBOX_PASSWORD"
         Hostname "$FRITZBOX_HOSTNAME"
         Verbose "$VERBOSE"
    </Module>
</Plugin>
EOF

exec /usr/sbin/collectd -f
