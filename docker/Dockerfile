FROM alpine

# Install collectd and dependencies for fritzcollectd.
RUN apk add --no-cache \
        collectd \
        collectd-python \
        collectd-network \
        python2 \
        py2-pip \
        py2-lxml \
        py2-pbr \
        git

# Copy entrypoint script.
COPY entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
