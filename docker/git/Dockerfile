FROM rockstorm/gitweb:2.45

COPY ./ansible /var/lib/git/ubuntu-config/ansible
COPY ./install.sh /var/lib/git/ubuntu-config/install.sh

WORKDIR /var/lib/git/ubuntu-config

RUN git init -b main && \
    git config user.email "test@test.com" && \
    git config user.name "Test Git" && \
    git add . && \
    git commit -m "Initial commit"

# Create sync scripts
COPY ./docker/git/commit-changes.sh /usr/local/bin/commit-changes.sh
RUN chmod +x /usr/local/bin/commit-changes.sh

# Add to cron every minutes seconds
RUN \
    mkdir /etc/cron.d && \
    touch /var/log/cron.log && \
    echo "* * * * * /usr/local/bin/commit-changes.sh > /proc/1/fd/1 2>/proc/1/fd/2" > /etc/cron.d/commit-changes && \
    chmod 0644 /etc/cron.d/commit-changes && \
    crontab /etc/cron.d/commit-changes

CMD ["/bin/sh","-c","cron && echo \"FCGI_GROUP=${GIT_GROUP}\" > /etc/default/fcgiwrap &&   envsubst '$GITWEB_BASE_PATH' < /etc/nginx/default.tmpl > /etc/nginx/sites-enabled/default &&   service fcgiwrap start &&   exec nginx"]

HEALTHCHECK --interval=5s --timeout=3s --retries=3 CMD ["curl", "-f", "http://localhost:80"]

USER git