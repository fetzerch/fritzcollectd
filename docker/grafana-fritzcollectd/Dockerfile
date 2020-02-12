FROM grafana/grafana

# Provide Grafana provisioning configuration for datasources and dashboards.
USER root
COPY datasources /etc/grafana/provisioning/datasources/
COPY dashboards /etc/grafana/provisioning/dashboards/

# Download fritzcollectd dashboard.
RUN mkdir -p /var/lib/grafana/dashboards; \
    wget https://grafana.com/api/dashboards/713/revisions/4/download -O /var/lib/grafana/dashboards/713.json; \
    sed -i -e 's/${DS_INFLUXDB_COLLECTD}/influxdb/g' /var/lib/grafana/dashboards/713.json

USER grafana
