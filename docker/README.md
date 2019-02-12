# Docker Image

## Building

Just run inside of the `docker` directory

```
docker build -t fritzcollectd .
```

Afterwards, you can run it in debug to see if everything works as expected:

```
docker run -it --rm -e VERBOSE=true \
  -e FRITZBOX_USER=<username> -e FRITZBOX_PASSWORD=<password> \
  fritzcollectd
```

The output should show the values read from the FritzBox. The Docker image is templated via
environment variables. For more information, please see `docker/entrypoint.sh`.

## Test with `docker-compose`

You can also spin up a whole Docker stack including InfluxDB and Grafana to play with:

```
FRITZBOX_USER=<username> FRITZBOX_PASSWORD=<password> docker-compose up --build -d
```

You can access the Grafana UI on `<your-docker-machine>:3000`, Chronograph runs on `:8888`.
