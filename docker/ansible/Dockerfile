FROM ubuntu:24.04 as base

RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# hadolint ignore=DL3008
RUN --mount=type=cache,target=/var/cache/apt,sharing=private \
    --mount=type=cache,target=/var/lib/apt,sharing=private \
    set -eu; \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common gnupg-agent sshpass wget pipx && \
    pipx ensurepath

RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /root/.ssh
WORKDIR /ansible

# Install pipx packages
RUN --mount=type=cache,target=/root/.cache/pipx,sharing=private \
    set -eu; \
    pipx install --include-deps ansible && \
    pipx inject --include-apps ansible jmespath

COPY ./ansible/requirements.yml /ansible/requirements.yml
RUN set -eu; \
    /root/.local/bin/ansible-galaxy install -r /ansible/requirements.yml

FROM base as ci

CMD ["tail", "-f", "/dev/null"]