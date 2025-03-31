FROM ubuntu:24.04 AS base

RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# hadolint ignore=DL3008
RUN --mount=type=cache,target=/var/cache/apt,sharing=private \
    --mount=type=cache,target=/var/lib/apt,sharing=private \
    set -eu; \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common gnupg-agent openssh-client sshpass wget pipx unzip vim && \
    pipx ensurepath

RUN mkdir -p /root/.ssh
WORKDIR /ansible

# Install pipx packages
# hadolint ignore=DL3013
RUN --mount=type=cache,target=/root/.cache/pipx,sharing=private \
    set -eu; \
    pipx install --include-deps ansible && \
    pipx inject --include-apps ansible jmespath

COPY ./ansible/requirements.yml /ansible/requirements.yml
RUN set -eu; \
    /root/.local/bin/ansible-galaxy install -r /ansible/requirements.yml

# Install Bitwarden CLI
RUN set -eu; \
    wget -q https://github.com/bitwarden/clients/releases/download/cli-v2024.2.0/bw-linux-2024.2.0.zip -O /tmp/bw-linux.zip && \
    unzip /tmp/bw-linux.zip -d /usr/local/bin && \
    chmod +x /usr/local/bin/bw

# Install Ansible Mitogen
RUN set -eu; \
    wget -q https://files.pythonhosted.org/packages/source/m/mitogen/mitogen-0.3.9.tar.gz -O /tmp/mitogen.tar.gz && \
    tar -xvf /tmp/mitogen.tar.gz -C /tmp && \
    mkdir -p /etc/ansible && \
    mv /tmp/mitogen-0.3.9 /etc/ansible/mitogen

HEALTHCHECK --interval=5s --timeout=3s --retries=3 CMD [ "ansible", "--version" ]

USER ansible

FROM base AS ci

CMD ["tail", "-f", "/dev/null"]

