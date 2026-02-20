FROM rockstorm/gitweb:2.52

# checkov:skip=CKV_DOCKER_8:nginx + gitweb need to be run as root
# hadolint ignore=DL3002
USER root

# hadolint ignore=DL3018
RUN apk add --no-cache bash

ARG GIT_SOURCE=/srv/source/ubuntu-config
ENV GIT_SOURCE=${GIT_SOURCE}

RUN set -xe \
    mkdir -p ${GIT_SOURCE} && \
    git config --global --add safe.directory '*' && \
    git config --system --add safe.directory '*'

WORKDIR ${GIT_SOURCE}

COPY ./ansible ${GIT_SOURCE}/ansible
COPY ./install.sh ${GIT_SOURCE}/install.sh

RUN git init -b main && \
    git config user.email "test@test.com" && \
    git config user.name "Test Git" && \
    git add . && \
    git commit -m "Initial commit"

# Create sync scripts
COPY ./docker/git/commit-changes.sh /usr/local/bin/commit-changes.sh
RUN chmod +x /usr/local/bin/commit-changes.sh

WORKDIR /srv/git

# Add to cron every minutes seconds
RUN touch crontab.tmp \
    && echo "* * * * * /usr/local/bin/commit-changes.sh > /proc/1/fd/1 2>/proc/1/fd/2" > crontab.tmp \
    && crontab crontab.tmp \
    && rm -rf crontab.tmp \
    && echo "ln -s ${GIT_SOURCE}/.git ubuntu-config.git &" >> /docker-entrypoint.d/50-start-fcgiwrap.sh \
    && echo "/usr/sbin/crond -f -d 0 &" >> /docker-entrypoint.d/50-start-fcgiwrap.sh

HEALTHCHECK --interval=5s --timeout=3s --retries=3 CMD ["curl", "-f", "http://localhost:80"]