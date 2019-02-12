FROM grafana/grafana

USER root

COPY datasources /etc/grafana/provisioning/datasources/
COPY dashboards /etc/grafana/provisioning/dashboards/

RUN \
    mkdir -p /var/lib/grafana/dashboards; \
    curl https://grafana.com/api/dashboards/713/revisions/4/download > /var/lib/grafana/dashboards/713.json; \
    sed -i -e 's/${DS_INFLUXDB_COLLECTD}/influxdb/g' /var/lib/grafana/dashboards/713.json

USER grafana
