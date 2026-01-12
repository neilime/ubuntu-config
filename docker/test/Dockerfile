FROM python:3.14-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# hadolint ignore=DL3008
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  bash \
  docker.io \
  openssh-client \
  sshpass \
  curl \
  wget \
  git \
  ca-certificates \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Create a non-root user for running tests
RUN useradd -m -s /bin/bash testuser && \
  mkdir -p /home/testuser/.ssh && \
  chown -R testuser:testuser /home/testuser && \
  mkdir -p /workspace/tests /workspace/vm

# Set working directory
WORKDIR /workspace

# Copy test requirements and install Python dependencies
COPY requirements.txt /workspace/requirements.txt
# hadolint ignore=DL3042
RUN pip3 install --no-cache-dir -r /workspace/requirements.txt

# Note: test files and vm will be mounted as volumes at runtime

# Set up SSH config for VM connections
USER testuser
RUN printf "Host *\\nStrictHostKeyChecking no\\nUserKnownHostsFile=/dev/null\\nLogLevel ERROR\\nIdentityFile ~/.ssh/id_rsa\\nIdentitiesOnly yes\\n" > /home/testuser/.ssh/config

# Create entrypoint script to handle SSH key setup at runtime  
USER root
RUN cat > /entrypoint.sh <<'EOF'
#!/bin/bash
# Setup SSH key if available
if [ -f /workspace/vm/id_rsa ]; then
  cp /workspace/vm/id_rsa /home/testuser/.ssh/id_rsa
  chmod 600 /home/testuser/.ssh/id_rsa
  if [ "$(id -u)" -eq 0 ]; then
    chown testuser:testuser /home/testuser/.ssh/id_rsa
  fi
fi

# Ensure pytest cache is writable when /workspace is a bind mount
if [ "$(id -u)" -eq 0 ]; then
  mkdir -p /workspace/tests/.pytest_cache
  chown -R testuser:testuser /workspace/tests/.pytest_cache
fi

# Execute command; when root, drop privileges to testuser.
if [ $# -eq 0 ]; then
  set -- python3 tests/run_tests.py
fi

if [ "$(id -u)" -eq 0 ]; then
  command_string=""
  for arg in "$@"; do
    command_string+="$(printf '%q ' "$arg")"
  done
  exec su -l testuser -c "cd /workspace && $command_string"
fi

exec "$@"
EOF

RUN chmod +x /entrypoint.sh

# Default to non-root; CI can override with `docker run --user root` when needed.
USER testuser

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python3 --version || exit 1

# Default command
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python3", "tests/run_tests.py"]