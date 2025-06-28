# Lima VM E2E Testing for ubuntu-config

This document describes how to use [Lima](https://lima-vm.io/) for end-to-end testing of the ubuntu-config project, both locally and in CI environments.

## Overview

Lima is a Linux virtual machine technology that provides consistent cross-platform virtualization for macOS, Linux, and Windows (via WSL2). It offers several advantages over the existing QEMU/Multipass setup:

- **Cross-platform consistency**: Works the same on macOS, Linux, and Windows
- **Lightweight**: Minimal resource overhead compared to traditional VMs
- **Cloud-init integration**: Easy VM provisioning and configuration
- **Container-like experience**: Fast startup and simple CLI interface
- **CI-friendly**: Designed for automation and scripting

## Prerequisites

### Local Development

- **macOS**: Install via Homebrew: `brew install lima`
- **Linux**: Follow [official installation guide](https://lima-vm.io/docs/installation/)
- **Windows**: Use WSL2 + Linux installation

### System Requirements

- **Minimum**: 4GB RAM, 2 CPU cores, 10GB disk space
- **Recommended**: 8GB RAM, 4 CPU cores, 20GB disk space
- **For Desktop testing**: 8GB+ RAM recommended

## Quick Start

### 1. Setup Lima Environment

```bash
# Run the setup script to check requirements and validate configurations
./scripts/lima-setup.sh
```

### 2. Run E2E Tests

```bash
# Server tests (lightweight, recommended for most cases)
make test-lima

# Desktop tests (includes GUI environment)
make test-lima-desktop

# CI-style tests (auto-cleanup after completion)
make test-lima-ci
```

### 3. Manual VM Management

```bash
# Start a server VM
limactl start --name=ubuntu-config-server lima/ubuntu-server-ci.yaml

# Start a desktop VM
limactl start --name=ubuntu-config-desktop lima/ubuntu-desktop.yaml

# Run commands in the VM
limactl shell ubuntu-config-server uname -a

# Get a shell in the VM
limactl shell ubuntu-config-server

# Run the ubuntu-config test
limactl shell ubuntu-config-server ~/run-ubuntu-config-test.sh

# Stop and delete the VM
limactl stop ubuntu-config-server
limactl delete ubuntu-config-server
```

## Configuration Files

### `lima/ubuntu-server-ci.yaml`

Lightweight configuration optimized for CI environments:
- 2 CPUs, 2GB RAM, 10GB disk
- Ubuntu 24.04 LTS Server
- Headless operation
- Essential packages only
- Fast provisioning

### `lima/ubuntu-desktop.yaml`

Full desktop environment for comprehensive GUI testing:
- 4 CPUs, 4GB RAM, 15GB disk
- Ubuntu 24.04 LTS Desktop
- Xvfb for headless GUI testing
- VNC support (optional)
- Complete desktop environment

## Scripts

### `scripts/lima-setup.sh`

Setup and validation script:
- Checks Lima installation
- Validates system requirements
- Tests configuration files
- Shows usage examples

### `scripts/lima-test.sh`

Comprehensive test runner:
- Creates and manages Lima VMs
- Runs ubuntu-config tests
- Collects results and logs
- Supports cleanup and CI modes

#### Options:

```bash
scripts/lima-test.sh [OPTIONS]

OPTIONS:
    -n, --name NAME         VM name (default: ubuntu-config-test)
    -t, --type TYPE         Config type: server or desktop (default: server)
    -d, --destroy           Destroy VM after test completion
    -s, --skip-provision    Skip provisioning if VM already exists
    -T, --timeout SECONDS  Test timeout in seconds (default: 1800)
    -h, --help              Show help message
```

## Makefile Targets

| Target | Description |
|--------|-------------|
| `setup-lima` | Run Lima setup and validation |
| `test-lima` | Run server-based E2E tests |
| `test-lima-desktop` | Run desktop-based E2E tests |
| `test-lima-ci` | Run tests with auto-cleanup |

## GitHub Actions Integration

### Workflow Files

- **`.github/workflows/__tests-lima.yml`**: Reusable Lima testing workflow
- **`.github/workflows/lima-e2e.yml`**: Standalone Lima E2E testing
- **`.github/workflows/__shared-ci.yml`**: Integrated with main CI

### Manual Testing

Trigger Lima tests manually via GitHub Actions:

1. Go to the "Actions" tab in the repository
2. Select "Lima E2E Testing" workflow
3. Click "Run workflow"
4. Choose options (desktop testing, timeout)

### Automated Testing

Lima server tests run automatically as part of the main CI pipeline. Desktop tests run daily via scheduled workflow.

## Environment Variables

The following environment variables can be used to customize testing:

- `REPOSITORY_URL`: Git repository URL (default: current repository)
- `REPOSITORY_BRANCH`: Git branch to test (default: current branch)
- `BITWARDEN_EMAIL`: Bitwarden email for testing (CI only)
- `BITWARDEN_PASSWORD`: Bitwarden password for testing (CI only)

## Troubleshooting

### Common Issues

#### Lima Not Starting

```bash
# Check Lima status
limactl list

# Check system logs
limactl info <vm-name>

# Verify system requirements
./scripts/lima-setup.sh
```

#### VM Creation Fails

```bash
# Clean up failed VMs
limactl delete --force <vm-name>

# Check available resources
free -h
df -h

# Try with smaller configuration
limactl start lima/ubuntu-server-ci.yaml
```

#### Tests Timeout

```bash
# Increase timeout
./scripts/lima-test.sh --timeout 3600

# Check VM status during test
limactl list
limactl shell <vm-name> top
```

#### Network Issues

```bash
# Check Lima network status
limactl info <vm-name>

# Test network connectivity
limactl shell <vm-name> ping google.com
```

### Performance Optimization

#### Linux (KVM acceleration)

```bash
# Ensure KVM is available
ls -la /dev/kvm

# Add user to kvm group
sudo usermod -a -G kvm $USER
```

#### macOS (Virtualization framework)

```bash
# Use Apple's native virtualization (requires macOS 12+)
# This is automatically used when available
```

#### Resource Management

```bash
# Limit parallel VMs
limactl prune --all

# Monitor resource usage
limactl list
htop
```

## Comparison with Existing Solutions

| Feature | Lima | QEMU/KVM (current) | Multipass (current) |
|---------|------|--------------------|--------------------|
| Cross-platform | ✅ | ❌ (Linux only) | ✅ |
| Resource efficiency | ✅ | ⚠️ | ✅ |
| Setup complexity | ✅ Low | ❌ High | ✅ Low |
| CI integration | ✅ | ✅ | ⚠️ |
| Desktop support | ✅ | ✅ | ✅ |
| Automation-friendly | ✅ | ⚠️ | ✅ |

## Limitations and Known Issues

### Current Limitations

1. **Apple Silicon**: Some features may be limited on M1/M2 Macs
2. **Windows**: Requires WSL2, may have performance limitations
3. **GPU acceleration**: Limited support for hardware GPU acceleration
4. **Nested virtualization**: May not work in all cloud environments

### Workarounds

1. Use server configuration for better compatibility
2. Increase timeouts for slower environments
3. Use software rendering for GUI tests
4. Fall back to existing QEMU/Multipass for specific cases

## Future Improvements

- [ ] Add support for ARM64 images
- [ ] Integrate with lima's built-in registry for faster image pulls
- [ ] Add GPU acceleration support for desktop testing
- [ ] Implement parallel test execution
- [ ] Add network isolation for multi-VM testing scenarios

## Contributing

When contributing Lima-related changes:

1. Test on both server and desktop configurations
2. Verify cross-platform compatibility
3. Update documentation for new features
4. Add appropriate error handling and logging

## Resources

- [Lima Official Documentation](https://lima-vm.io/docs/)
- [Lima GitHub Repository](https://github.com/lima-vm/lima)
- [Cloud-init Documentation](https://cloud-init.readthedocs.io/)
- [Ubuntu Cloud Images](https://cloud-images.ubuntu.com/)