# fritzcollectd - Docker Image

This directory contains Docker support configuration for fritzcollectd.

A `Dockerfile` simplifies the deployment of fritzcollectd for example into an
existing environment with an already running Grafana and InfluxDB.

In addition we also provide a `docker-compose.yaml` that allows to spin
up Grafana, InfluxDB and collectd with the current development version
of fritzcollectd.

## Standalone Docker image

The standalone Docker image is built with:

```
docker build -t fritzcollectd .
```

Afterwards the image can be run with:

```
docker run --rm \
    --env FRITZBOX_HOST=<ip> \
    --env FRITZBOX_USER=<username> \
    --env FRITZBOX_PASSWORD=<password> \
    --env VERBOSE=true \
    fritzcollectd
```

The Docker image can be configured through environment variables.
See `docker/entrypoint.sh` for more information.

## Full Grafana, InfluxDB, collectd stack with `docker-compose`

The following command allows to spin up a whole Docker based stack including
a preconfigured Grafana and InfluxDB to play with:

```
FRITZBOX_USER=<username> FRITZBOX_PASSWORD=<password> docker-compose up --build --detach
```

You can access the Grafana UI on `<your-docker-host>:3000`.
