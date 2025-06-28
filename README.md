# ubuntu-config

My own Ubuntu setup &amp; config. This project uses Ansible to set up and configure a personal computer running on Ubuntu.

## Prerequisites

- Ubuntu machine for the setup

## Execute installation

```sh
wget -qO- "https://raw.githubusercontent.com/neilime/ubuntu-config/main/install.sh" | sh
```

## Project Structure

The project has the following structure:

```txt
ubuntu-config
├── .github
│   └── workflows: GitHub Actions workflows for CI
├── docker: Dockerfiles to build dev/ci images
├── ansible: Ansible roles and playbooks
└── README.md
```

## Development

1. Clone the repository:

```bash
git clone https://github.com/neilime/ubuntu-config.git
cd ubuntu-config
```

2. Setup the development stack:

```bash
make setup
```

3. Test the install script:

```bash

# On docker container
make test-docker

# Pass env variables to the script
make test-docker -- "--env SKIP_INSTALL_REQUIREMENTS=true --env SETUP_TAGS=keys --env SKIP_CLEANUP=true"

# On virtual machine (Multipass)
make test-vm

# On Lima VM (cross-platform, recommended)
make test-lima

# On Lima VM with desktop environment
make test-lima-desktop
```

This will run the setup role on your Ubuntu machine.

### Lima VM Testing

This project supports Lima VMs for cross-platform E2E testing. Lima provides consistent virtualization across macOS, Linux, and Windows.

#### Prerequisites

- Install Lima: `brew install lima` (macOS) or see [Lima installation guide](https://lima-vm.io/docs/installation/)

#### Quick Start

```bash
# Setup Lima environment
make setup-lima

# Run lightweight server tests
make test-lima

# Run comprehensive desktop tests (requires more resources)
make test-lima-desktop
```

For detailed Lima testing documentation, see [docs/lima-testing.md](docs/lima-testing.md).

## Continuous Integration

This project uses GitHub Actions to test the Ansible playbook. The workflow is defined in `.github/workflows/main-ci.yml`. It checks out the code and runs the Ansible playbook on Ubuntu machines using multiple approaches:

- **Docker containers**: Fast, lightweight testing
- **QEMU/KVM VMs**: Full virtualization testing
- **Lima VMs**: Cross-platform VM testing

The workflow is triggered on every push to the repository.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
