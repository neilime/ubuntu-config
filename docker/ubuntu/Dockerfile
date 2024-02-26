FROM kasmweb/ubuntu-jammy-dind:1.14.0

USER root

RUN --mount=type=cache,target=/var/cache/apt,sharing=private \
    --mount=type=cache,target=/var/lib/apt,sharing=private \
    set -eu; \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get install -y --no-install-recommends ubuntu-desktop xcb qt5dxcb-plugin

# FIXME: install Bitwarden CLI as we cannot install it with snap
RUN set -eu; \
    wget https://github.com/bitwarden/clients/releases/download/cli-v2024.2.0/bw-linux-2024.2.0.zip -O /tmp/bw-linux.zip && \
    unzip /tmp/bw-linux.zip -d /usr/local/bin && \
    chmod +x /usr/local/bin/bw

RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

ENV USER=kasm-user

USER 1000
