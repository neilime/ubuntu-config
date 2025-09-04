# ubuntu-config

My own Ubuntu setup & config. This project uses Ansible to set up and configure a
personal computer running on Ubuntu.

## Prerequisites

- Ubuntu machine for the setup

## Execute installation

```sh
wget -qO- \
"https://raw.githubusercontent.com/neilime/ubuntu-config/main/install.sh" | sh
```

## Project Structure

The project has the following structure:

```txt
ubuntu-config
├── .github
│   └── workflows: GitHub Actions workflows for CI
├── docker: Dockerfiles to build dev/ci images
├── ansible: Ansible roles and playbooks
├── tests: TestInfra test suite for validation
└── README.md
```

## Features

- [APT packages management](./ansible/roles/setup_apt/README.md).
- [SSH and GPG keys management](./ansible/roles/setup_keys/README.md).
- [Snap packages management](./ansible/roles/setup_snap/README.md).

## Development

### Prerequisites

For local development, you'll need:

- Docker and Docker Compose
- [Lima](https://github.com/lima-vm/lima) for VM testing (consistent with CI/CD)

#### Installing Lima

**macOS:**
```bash
brew install lima
```

**Linux:**
```bash
# See https://github.com/lima-vm/lima#getting-started for latest instructions
curl -fsSL https://get.lima.sh | sh
```

### Setup

1. Clone the repository:

```bash
git clone https://github.com/neilime/ubuntu-config.git
cd ubuntu-config
```

2. Setup the development stack:

```bash
make setup
```

### Local Testing

#### Docker Testing (Fast)

```bash
# Run the install script in Docker container
make docker-install-script

# Pass env variables to the script
make docker-install-script -- \
"--env SKIP_INSTALL_REQUIREMENTS=true --env SETUP_TAGS=keys --env SKIP_CLEANUP=true"

# Run tests
make docker-test
```

#### VM Testing with Lima (Matches CI/CD)

Local VM testing now uses Lima VMs (consistent with CI/CD) instead of Multipass:

```bash
# Setup Lima VM (first time or after vm-down)
make vm-setup

# Run the install script on VM
make vm-install-script

# Run tests on VM  
make vm-test

# Access VM shell
make vm-shell

# Reset VM to clean state
make vm-restore

# Stop and remove VM
make vm-down
```

## Continuous Integration

This project uses GitHub Actions to test the Ansible playbook with TestInfra using both Docker containers and Lima VMs. The workflows are defined in `.github/workflows/`.

### Test Workflows

- `__tests-docker.yml` - Tests the setup in Docker containers using the test service
- `__tests-vm.yml` - Tests the setup in Lima virtual machines (matching local development)
- `__shared-ci.yml` - Shared CI workflow that builds test images and orchestrates tests
- `main-ci.yml` - Main CI workflow that triggers all tests

Both local development and CI/CD use Lima VMs for consistency, ensuring that:
- Local testing environment matches CI/CD exactly
- Issues caught locally will be caught in CI/CD
- VM configurations are shared between environments

The TestInfra test suite runs in a dedicated Docker service and provides comprehensive validation of:

- Package installation and configuration
- Service status and functionality
- File permissions and configurations
- User environment setup
- Development tool installations

Tests are triggered on every push to the repository and provide detailed reports on the system configuration status.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to
discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
