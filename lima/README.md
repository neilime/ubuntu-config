# Lima Examples for ubuntu-config

This directory contains example Lima configurations and scripts for testing ubuntu-config.

## Quick Start Example

Create a simple Lima VM and test ubuntu-config:

```bash
# 1. Start a Lima VM with ubuntu-config
lima start --name=my-test lima/ubuntu-server-ci.yaml

# 2. Wait for VM to be ready
lima my-test echo "VM is ready"

# 3. Run ubuntu-config test
lima my-test ~/run-ubuntu-config-test.sh

# 4. Check results
lima my-test cat /tmp/test-results/e2e-success

# 5. Cleanup
lima delete my-test
```

## Custom Configuration Example

You can customize the Lima configurations for your specific needs:

```yaml
# custom-config.yaml
cpus: 2
memory: "3GiB"
disk: "12GiB"

images:
  - location: "https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img"
    arch: "x86_64"

mounts:
  - location: "."
    mountPoint: "/home/ubuntu/ubuntu-config"
    writable: true

provision:
  - mode: system
    script: |
      apt-get update
      apt-get install -y python3-pip pipx git
  - mode: user
    script: |
      pipx install ansible
```

Then use it:

```bash
lima start --name=custom custom-config.yaml
```

## Environment Variables

You can customize the testing environment:

```bash
# Test a specific branch
REPOSITORY_BRANCH=feature-branch make test-lima

# Test a different repository
REPOSITORY_URL=https://github.com/myuser/my-fork.git make test-lima

# Combined
REPOSITORY_URL=https://github.com/myuser/my-fork.git \
REPOSITORY_BRANCH=my-feature \
make test-lima
```

## Advanced Usage

### Multiple VMs

```bash
# Start multiple VMs for parallel testing
lima start --name=test1 lima/ubuntu-server-ci.yaml
lima start --name=test2 lima/ubuntu-server-ci.yaml

# Run tests in parallel
lima test1 ~/run-ubuntu-config-test.sh &
lima test2 ~/run-ubuntu-config-test.sh &
wait

# Cleanup
lima delete test1 test2
```

### Development Workflow

```bash
# Create a long-running development VM
lima start --name=dev lima/ubuntu-desktop.yaml

# Make changes to ubuntu-config locally
# Test changes in the VM
lima dev ~/run-ubuntu-config-test.sh

# Get a shell for debugging
lima dev

# Keep VM running for iterative development
```

## See Also

- [Lima Testing Documentation](../docs/lima-testing.md)
- [Lima Official Documentation](https://lima-vm.io/docs/)
- [Project README](../README.md)