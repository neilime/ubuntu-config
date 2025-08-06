# TestInfra Test Suite

This directory contains a comprehensive test suite using TestInfra
(pytest-testinfra) to validate the Ansible configuration setup.

## Overview

The test suite provides automated validation of system configuration, package
installation, service status, and development environment setup through
**81 tests** organized in **6 test modules**.

## Test Service Architecture

The tests are designed to run in a dedicated Docker service built from a
lightweight Python image, providing:

- **Container-only execution** eliminating local test dependencies
- **Multi-host testing** support for Docker containers, VMs, and SSH connections
- **Pre-configured SSH setup** for seamless VM testing with auto-generated keys
- **Environment-agnostic** design working across local, Docker, and VM
  environments

## Usage

### Running Tests with Test Service

```bash
# Run all tests in Docker environment using test service
make test-docker

# Run specific test categories using test service
docker compose run --rm test python3 -m pytest -m apt      # Only APT tests
docker compose run --rm test python3 -m pytest -m dev      # Only dev tools

# Remote testing via SSH using test service
docker compose run --rm test python3 tests/run_tests.py \
--host="ssh://user@hostname" --user="username"
```

### Test Categories

The test suite uses pytest markers to categorize tests:

- `apt` - APT packages and repositories
- `dev` - Development tools (Docker, Node.js, PHP, Git)
- `config` - System configuration (locale, timezone, utilities)
- `shell` - Shell configuration (Zsh, Oh My Zsh, aliases, Starship)
- `snap` - Snap packages and system
- `keys` - SSH and GPG keys management

### Available Options

```bash
# Verbose output
docker compose run --rm test python3 -m pytest -v

# Generate HTML report
docker compose run --rm test python3 -m pytest --html=test-report.html \
--self-contained-html

# Run tests in parallel
docker compose run --rm test python3 -m pytest -n auto

# Run specific test file
docker compose run --rm test python3 -m pytest tests/test_apt.py
```

## Test Coverage

### APT Tests (`test_apt.py`) - 20 tests

- Validates APT repositories and PPA configuration
- Checks installation of required packages
- Verifies package cache and sources

### Configuration Tests (`test_configuration.py`) - 13 tests

- Validates locale configuration (en_US.UTF-8)
- Checks timezone settings
- Verifies utility installations and configuration
- Tests system cleaning tools

### Development Tools Tests (`test_dev.py`) - 16 tests

- Validates Docker installation and service status
- Checks Node.js, PHP, and Git configurations
- Verifies development package installations
- Tests package manager configurations

### Keys Tests (`test_keys.py`) - 8 tests

- Validates SSH key configuration and permissions
- Checks GPG key setup and trust store
- Verifies key management utilities

### Shell Tests (`test_shell.py`) - 13 tests

- Validates Zsh installation and configuration
- Checks Oh My Zsh setup and themes
- Verifies shell aliases and custom configurations
- Tests Starship prompt configuration

### Snap Tests (`test_snap.py`) - 11 tests

- Validates snapd installation and service status
- Checks snap package installations
- Verifies snap configurations and permissions

## Best Practices

The test suite follows these best practices:

- **Consistent environments**: All tests run in the same containerized environment
- **Parameterized tests**: Efficient validation of multiple packages/configurations
- **Flexible host connections**: Support for local, Docker, and SSH testing
- **Clear test organization**: Logical grouping by functionality
- **Comprehensive coverage**: Tests all aspects of the Ansible configuration
- **CI integration**: Seamless integration with GitHub Actions workflows

## Integration with CI

The test service is built and deployed through the shared CI workflow, ensuring
consistent test environments across all CI runs. The Docker image is built from
`docker/test/Dockerfile` and used by both Docker and VM test workflows.
