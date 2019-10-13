#!/bin/sh

# InfluxDB configuration.
INFLUXDB_HOST=${INFLUXDB_HOST:-influxdb}
INFLUXDB_PORT=${INFLUXDB_PORT:-25826}

# fritzcollectd plugin configuration.
FRITZBOX_HOST=${FRITZBOX_HOST:-fritz.box}
FRITZBOX_PORT=${FRITZBOX_PORT:-49000}
FRITZBOX_USER=${FRITZBOX_USER:-dslf-config}
FRITZBOX_HOSTNAME=${FRITZBOX_HOSTNAME:-fritzbox}
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
    ModulePath "/fritzcollectd"
    Import "fritzcollectd"
    LogTraces true

    <Module fritzcollectd>
        Address "$FRITZBOX_HOST"
        Port $FRITZBOX_PORT
        User "$FRITZBOX_USER"
        Password "$FRITZBOX_PASSWORD"
        Hostname "$FRITZBOX_HOSTNAME"
        Instance "$INSTANCE"
        Verbose "$VERBOSE"
    </Module>
</Plugin>
EOF

# This container supports running with fritzcollectd's git repository mounted
# to /fritzcollectd (and we then just install the dependencies).
if [ -d "/fritzcollectd" ]; then
    pip install -r/fritzcollectd/requirements.txt
else
    pip install fritzcollectd
fi

exec /usr/sbin/collectd -f
