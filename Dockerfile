FROM ubuntu:22.04

# hadolint ignore=DL3008
RUN set -e; \
    apt-get update -y; \
    apt-get install -yq sudo init software-properties-common snapd dbus-x11 wget lighttpd; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*;

# Fine-tune the image to work as a desktop ubuntu installation
RUN touch /boot/vmlinuz-test;

SHELL ["/bin/bash","-o", "pipefail", "-c"]
RUN set -e; \ 
    useradd -m docker; \
    echo "docker:docker" | chpasswd; \
    adduser docker sudo; \
    echo "docker ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/docker;

COPY docker/lighttpd.conf /etc/lighttpd/lighttpd.conf

COPY docker/test.sh /test.sh
RUN chmod +x /test.sh

WORKDIR /home/docker
ENV REPOSITORY_URL=http://localhost:80
USER docker

STOPSIGNAL SIGRTMIN+3

# Start lighttpd
CMD ["lighttpd", "-D", "-f", "/etc/lighttpd/lighttpd.conf"]