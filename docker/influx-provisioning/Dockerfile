FROM docker_fritzcollectd

FROM influxdb:alpine

COPY --from=0 /usr/share/collectd/types.db /usr/share/collectd/types.db

COPY influxdb.conf /etc/influxdb
