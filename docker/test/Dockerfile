FROM python:3.13-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# hadolint ignore=DL3008
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
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
RUN printf "Host *\\nStrictHostKeyChecking no\\nUserKnownHostsFile=/dev/null\\nLogLevel ERROR\\n" > /home/testuser/.ssh/config

# Create entrypoint script to handle SSH key setup at runtime  
USER root
RUN printf '#!/bin/bash\\n# Setup SSH key if available\\nif [ -f /workspace/vm/id_rsa ]; then\\n    cp /workspace/vm/id_rsa /home/testuser/.ssh/id_rsa\\n    chmod 600 /home/testuser/.ssh/id_rsa\\n    chown testuser:testuser /home/testuser/.ssh/id_rsa\\nfi\\n\\n# Switch to testuser and execute command\\nif [ $# -eq 0 ]; then\\n    exec su testuser -c "python3 tests/run_tests.py --help"\\nelse\\n    exec su testuser -c "$*"\\nfi\\n' > /entrypoint.sh && chmod +x /entrypoint.sh

# Switch to testuser for final layer
USER testuser

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python3 --version || exit 1

# Default command
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python3", "tests/run_tests.py", "--help"]