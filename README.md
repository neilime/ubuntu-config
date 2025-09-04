# ubuntu-config

My own Ubuntu setup & config. This project uses Clean Architecture principles to create a layered, reproducible development environment using Ansible, Nix, and Home Manager.

## Architecture Overview

This setup follows **Clean Architecture** with three distinct layers:

### 🖥️ Host Layer (Ubuntu + Ansible)
- **Purpose**: Essential system packages and core OS configuration
- **Technology**: APT packages via Ansible
- **Scope**: System-wide, requires root access
- **Examples**: Core utilities, system services, hardware drivers

### 🏠 User Layer (Home Manager)
- **Purpose**: User-specific configurations and dotfiles
- **Technology**: Nix + Home Manager
- **Scope**: User-specific, declarative configuration
- **Examples**: Shell configs, Git settings, development tools, fonts

### 📁 Project Layer (Nix Flakes)
- **Purpose**: Project-specific development environments
- **Technology**: Nix flakes + direnv
- **Scope**: Per-repository, isolated environments
- **Examples**: Node.js versions, Python environments, project dependencies

## Prerequisites

- Ubuntu machine for the setup
- Internet connection for package downloads

## Quick Start

```sh
wget -qO- \
"https://raw.githubusercontent.com/neilime/ubuntu-config/main/install.sh" | sh
```

## Layer-Specific Installation

You can install specific layers using Ansible tags:

```bash
# Host layer only (system essentials)
ansible-playbook setup.yml --tags "base,host"

# Desktop layer (GUI applications)
ansible-playbook setup.yml --tags "desktop,flatpak"

# User layer (dotfiles and user configs)
ansible-playbook setup.yml --tags "user,home-manager"

# Project layer (Nix for development)
ansible-playbook setup.yml --tags "nix,project"

# Legacy compatibility
ansible-playbook setup.yml --tags "legacy"
```

## Project Structure

```txt
ubuntu-config
├── .github/
│   └── workflows/          # GitHub Actions workflows for CI
├── ansible/
│   ├── roles/
│   │   ├── setup_base/     # Host layer: system essentials
│   │   ├── setup_flatpak/  # Desktop layer: Flatpak apps
│   │   ├── setup_desktop/  # Desktop layer: GUI utilities
│   │   ├── setup_nix/      # Project layer: Nix bootstrap
│   │   ├── setup_home_manager/  # User layer: Home Manager setup
│   │   └── setup_*/        # Legacy roles (maintained for compatibility)
│   ├── group_vars/         # Configuration variables by layer
│   └── setup.yml           # Main playbook with clean architecture
├── home/
│   ├── flake.nix          # Home Manager Nix flake
│   └── home.nix           # User layer configuration
├── tests/                 # TestInfra validation per layer
└── docker/               # Development and CI containers
```

## Features by Layer

### Host Layer
- [Essential system packages](./ansible/roles/setup_base/vars/main.yml)
- [APT repository management](./ansible/roles/setup_apt/README.md)
- System services and core utilities

### Desktop Layer  
- [Flatpak applications](./ansible/roles/setup_flatpak/vars/main.yml) (replaces most Snap packages)
- [Desktop utilities](./ansible/roles/setup_desktop/vars/main.yml)
- GUI application management

### User Layer
- [Shell configuration (ZSH)](./home/home.nix) via Home Manager
- [Git configuration](./home/home.nix) with signing and includes
- [Development tools](./home/home.nix) (neovim, tmux, direnv)
- [SSH and GPG keys management](./ansible/roles/setup_keys/README.md)

### Project Layer
- Nix package manager with flakes support
- Per-project development environments
- direnv integration for automatic environment activation

### Legacy Support
- [Snap packages](./ansible/roles/setup_snap/README.md) (being phased out)
- Backward compatibility with existing configurations

## Development

### Setup Development Environment

1. Clone the repository:

```bash
git clone https://github.com/neilime/ubuntu-config.git
cd ubuntu-config
```

2. Setup the development stack:

```bash
make setup
```

### Testing the Configuration

#### Test Complete Setup
```bash
# Test on Docker container (fast, for development)
make docker-install-script

# Test on virtual machine (full environment)
make vm-install-script
```

#### Test Specific Layers
```bash
# Test only host layer
make docker-install-script -- "--env SETUP_TAGS=base,host"

# Test only desktop layer
make docker-install-script -- "--env SETUP_TAGS=desktop,flatpak"

# Test only user layer
make docker-install-script -- "--env SETUP_TAGS=user,home-manager"

# Test legacy compatibility
make docker-install-script -- "--env SETUP_TAGS=legacy"
```

#### Run Validation Tests
```bash
# Run all tests
make docker-tests

# Run layer-specific tests
pytest tests/test_base.py      # Host layer
pytest tests/test_flatpak.py   # Desktop layer (Flatpak)
pytest tests/test_nix.py       # Project layer (Nix)
pytest tests/test_home_manager.py  # User layer
```

### Using Home Manager (User Layer)

After installation, you can manage user configurations with Home Manager:

```bash
# Switch to new configuration
cd ~/.config/home-manager
home-manager switch --flake .#$(whoami)

# Edit your configuration
vim ~/.config/home-manager/home.nix
home-manager switch --flake .#$(whoami)
```

### Creating Project Environments (Project Layer)

For project-specific environments, use the provided templates:

```bash
# Copy template to your project
cp -r ~/Documents/project-template/* /path/to/your/project/
cd /path/to/your/project

# Enable direnv (automatic environment activation)
direnv allow

# Customize flake.nix for your project needs
vim flake.nix
```

### Migration from Legacy Setup

If upgrading from the old configuration:

1. **Backup existing configs**: Your current setup will be preserved
2. **Install new layers gradually**:
   ```bash
   # Start with project layer (least disruptive)
   ansible-playbook setup.yml --tags "nix,project"
   
   # Add user layer (optional, can coexist with existing configs)
   ansible-playbook setup.yml --tags "home-manager,user"
   
   # Migrate to desktop layer when ready
   ansible-playbook setup.yml --tags "flatpak,desktop"
   ```
3. **Validate each layer**: Test functionality before proceeding to next layer

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
