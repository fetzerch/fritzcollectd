FROM influxdb:alpine

# Enable InfluxDB's collectd listener.
ENV INFLUXDB_COLLECTD_ENABLED=true

# Download the collectd types collection.
RUN mkdir -p /usr/share/collectd/types; \
    wget https://raw.githubusercontent.com/collectd/collectd/master/src/types.db -O /usr/share/collectd/types.db
