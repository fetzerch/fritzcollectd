FROM debian:stretch-slim

# install collectd
RUN \
    apt-get update -qq; \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -qq \
        collectd \
        libpython2.7 \
        python-setuptools \
        python-wheel \
        python-pip; \
    apt-get clean; \
    rm -f /var/lib/apt/lists/deb* /var/lib/apt/lists/sec*


RUN pip install fritzcollectd

COPY entrypoint.sh /
RUN chmod 755 /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]
