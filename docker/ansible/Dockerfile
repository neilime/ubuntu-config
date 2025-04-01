FROM ubuntu:24.04 AS base

RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# hadolint ignore=DL3008
RUN --mount=type=cache,target=/var/cache/apt,sharing=private \
    --mount=type=cache,target=/var/lib/apt,sharing=private \
    set -eu; \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common gnupg-agent openssh-client sshpass wget pipx unzip vim    

RUN mkdir -p /root/.ssh

# Install Bitwarden CLI - https://github.com/bitwarden/clients/releases
ARG BW_VERSION=2025.2.0
RUN set -eu; \
    wget -q https://github.com/bitwarden/clients/releases/download/cli-v$BW_VERSION/bw-linux-$BW_VERSION.zip -O /tmp/bw-linux.zip && \
    unzip /tmp/bw-linux.zip -d /usr/local/bin && \
    chmod +x /usr/local/bin/bw

# Install Ansible Mitogen - https://github.com/mitogen-hq/mitogen/releases
ARG MITOGEN_VERSION=0.3.22
RUN set -eu; \
    mkdir -p /usr/share/ansible/plugins && \
    wget -q https://files.pythonhosted.org/packages/source/m/mitogen/mitogen-$MITOGEN_VERSION.tar.gz -O /tmp/mitogen.tar.gz && \
    tar -xvf /tmp/mitogen.tar.gz -C /tmp && \    
    mv /tmp/mitogen-$MITOGEN_VERSION /usr/share/ansible/plugins/mitogen

WORKDIR /ansible
USER ubuntu

# Install pipx packages
# hadolint ignore=DL3013
RUN --mount=type=cache,target=~/.cache/pipx,sharing=private \
    set -eu; \
    pipx install --include-deps ansible ansible-lint && \
    pipx inject --include-apps ansible jmespath && \
    pipx ensurepath

COPY ./ansible/requirements.yml /ansible/requirements.yml
RUN set -eu; \
    ~/.local/bin/ansible-galaxy install -r /ansible/requirements.yml

HEALTHCHECK --interval=5s --timeout=3s --retries=3 CMD [ "/home/ubuntu/.local/bin/ansible", "--version" ]

FROM base AS ci

CMD ["tail", "-f", "/dev/null"]

