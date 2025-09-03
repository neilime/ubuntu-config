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

1. Clone the repository:

```bash
git clone https://github.com/neilime/ubuntu-config.git
cd ubuntu-config
```

1. Setup the development stack:

```bash
make setup
```

1. Test the install script:

```bash
# On docker container
make test-docker

# Pass env variables to the script
make test-docker -- \
"--env SKIP_INSTALL_REQUIREMENTS=true --env SETUP_TAGS=keys --env SKIP_CLEANUP=true"

# On virtual machine
make test-vm
```

## Continuous Integration

This project uses GitHub Actions to test the Ansible playbook with TestInfra using
a dedicated test service architecture. The workflows are defined in
`.github/workflows/`.

### Test Workflows

- `__tests-docker.yml` - Tests the setup in Docker containers using the test
  service
- `__tests-vm.yml` - Tests the setup in virtual machines using the test service
- `__shared-ci.yml` - Shared CI workflow that builds test images and orchestrates
  tests
- `main-ci.yml` - Main CI workflow that triggers all tests

The TestInfra test suite runs in a dedicated Docker service and provides
comprehensive validation of:

- Package installation and configuration
- Service status and functionality
- File permissions and configurations
- User environment setup
- Development tool installations

Tests are triggered on every push to the repository and provide detailed reports
on the system configuration status.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to
discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
