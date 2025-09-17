# ubuntu-config

My own Ubuntu setup & config. This project uses Clean Architecture principles with domain-driven design to create a layered, reproducible development environment using Ansible, Nix, and Home Manager.

## Quick Start

Get your Ubuntu system configured with everything you need in one command:

```sh
wget -qO- \
"https://raw.githubusercontent.com/neilime/ubuntu-config/main/install.sh?$(date +%s)" | sh
```

### Requirements

- A fresh Ubuntu 22.04+ installation (tested on 22.04 and 24.04)
- An internet connection
- A user account with `sudo` privileges
- Bitwarden account credentials for secure password management

### What It Does

This single script will automatically:

- Install all essential system packages and development tools
- Configure your desktop environment with GNOME preferences
- Set up development environments with Nix and Home Manager
- Install applications across all domains (browser, communication, media, utilities)
- Configure your shell, Git, SSH keys, and development environment

For domain-specific installations or customization options, see the [Domain-Specific Installation](#specific-installation) section below.

### Specific Installation

You can install specific domains or layers using tags. For example, to install only the system tools:

```sh
wget -qO- "https://raw.githubusercontent.com/neilime/ubuntu-config/main/install.sh?$(date +%s)" | sh -s -- --env SETUP_TAGS=system
```

## Architecture Overview

This setup follows domain-driven design and three distinct layers:

### 🖥️ System Layer (Ubuntu + Ansible)

- **Purpose**: Essential system packages and core OS configuration
- **Technology**: APT packages and system services via Ansible
- **Scope**: System-wide, requires root access
- **Domain**: System essentials managed by `setup_system` role
- **Examples**: Core utilities, system services, hardware drivers, GNOME preferences

### 🏠 User Layer (Home Manager)

- **Purpose**: User-specific configurations and dotfiles
- **Technology**: Nix + Home Manager with templated configuration
- **Scope**: User-specific, declarative configuration
- **Domain**: User environment managed by `setup_home_manager` role
- **Examples**: Shell configs, Git settings, development tools, fonts

### 📁 Project Layer (Nix Flakes)

- **Purpose**: Project-specific development environments
- **Technology**: Nix flakes + direnv
- **Scope**: Per-repository, isolated environments
- **Examples**: Node.js versions, Python environments, project dependencies

### Application Domains

The setup is organized by functional domains, each managed by dedicated roles:

- **🛡️ System** (`setup_system`): Core system packages and services
- **🌐 Browser** (`setup_browser`): Web browsers and browsing tools
- **💬 Communication** (`setup_communication`): Messaging and collaboration apps
- **⚙️ Development** (`setup_development`): Development tools and environments
- **🎵 Media** (`setup_media`): Audio, video, and multimedia applications
- **🛠️ Utility** (`setup_utility`): System utilities and security tools
- **🏠 Home Manager** (`setup_home_manager`): User configuration management
- **🔑 Keys Management** (`setup_keys`): SSH and GPG key handling

## Domain Configuration

All application domains are centrally configured in [`ansible/group_vars/all.yml`](./ansible/group_vars/all.yml) with a consistent structure:

```yaml
domain_name:
  apt: # APT packages for the domain
  flatpak: # Flatpak applications for the domain
  repositories: # APT repositories needed for the domain
  favorites: # Applications to pin to GNOME launcher
```

This domain-driven approach provides:

- **Separation of Concerns**: Each domain manages its own packages and configuration
- **Centralized Management**: All configuration in one place for easy maintenance
- **Selective Installation**: Install only the domains you need using tags
- **Consistent Structure**: Predictable configuration format across all domains

## Project Structure

```txt
ubuntu-config
├── .github/
│   └── workflows/          # GitHub Actions workflows for CI
├── ansible/
│   ├── roles/
│   │   ├── setup_system/    # System layer: essential packages & configuration
│   │   ├── setup_development/  # Development domain: dev tools & environment
│   │   ├── setup_browser/   # Browser domain: web browsers
│   │   ├── setup_communication/  # Communication domain: messaging apps
│   │   ├── setup_media/     # Media domain: multimedia applications
│   │   ├── setup_utility/   # Utility domain: system utilities & security tools
│   │   ├── setup_home_manager/  # User layer: Home Manager setup
│   │   ├── setup_keys/      # User layer: SSH/GPG key management
│   │   └── gnome_favorites/ # Shared: GNOME launcher pinning
│   ├── group_vars/          # Centralized domain-based configuration
│   └── setup.yml            # Main playbook with domain architecture
├── home/
│   ├── flake.nix           # Home Manager Nix flake
│   └── home.nix.j2         # User layer configuration template
├── tests/                  # Domain-based TestInfra validation with Gherkin
├── legacy/                 # Historical configurations and deprecated roles
├── vm/                     # Lima VM configuration for testing
└── docker/                # Development and CI containers
```

## Features by Domain

### System Layer

- [Essential system packages](./ansible/group_vars/all.yml) (system.apt)
- System services and core utilities
- Timezone and locale configuration
- GNOME desktop environment preferences

### Development Domain

- [Development tools via Nix](./ansible/group_vars/all.yml) (development.nix_packages)
- [Development Flatpak applications](./ansible/group_vars/all.yml) (development.flatpak)
- [APT repositories for development](./ansible/group_vars/all.yml) (development.repositories)
- Projects directory setup

### Browser Domain

- [Web browsers via Flatpak](./ansible/group_vars/all.yml) (browser.flatpak)
- Browser application management

### Communication Domain

- [Communication apps via Flatpak](./ansible/group_vars/all.yml) (communication.flatpak)
- Messaging and collaboration tools

### Media Domain

- [Media applications via Flatpak](./ansible/group_vars/all.yml) (media.flatpak)
- Audio and video players

### Utility Domain

- [System utilities via APT and Flatpak](./ansible/group_vars/all.yml) (utility.apt, utility.flatpak)
- [Security tools](./ansible/group_vars/all.yml) (Bitwarden password manager)
- System maintenance and backup tools

### User Layer

- [Shell configuration (Zsh)](./home/home.nix.j2) via Home Manager template
- [Git configuration](./ansible/group_vars/all.yml) (development.git) with signing and aliases
- [Development environment variables](./ansible/group_vars/all.yml) (development.environment)
- [SSH and GPG keys management](./ansible/roles/setup_keys/README.md)

### Project Layer

- Nix package manager with flakes support via Galaxy role
- Per-project development environments
- direnv integration for automatic environment activation

## Development

### Prerequisites

For local development, you'll need:

- Docker and Docker Compose
- [Lima](https://github.com/lima-vm/lima) for VM testing (consistent with CI/CD)
  - Installation guide: <https://lima-vm.io/docs/installation/>

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

### Local Testing

#### Docker Testing (Fast)

```bash
# Run the install script in Docker container
# Test on Docker container (fast, for development)
make docker-install-script

# Pass env variables to the script
make docker-install-script -- \
"--env SKIP_INSTALL_REQUIREMENTS=true --env SETUP_TAGS=system --env SKIP_CLEANUP=true"

# Run tests
make docker-test
```

#### VM Testing with Lima (Matches CI/CD)

Local VM testing now uses Lima VMs (consistent with CI/CD) instead of Multipass:

#### Run Validation Tests

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

### Using Home Manager (User Layer)

After installation, you can manage user configurations with Home Manager. The configuration is generated from a template using centralized variables:

```bash
# Switch to new configuration
cd ~/.config/home-manager
home-manager switch --flake .#$(whoami)

# Edit centralized configuration (affects template generation)
vim /home/runner/work/ubuntu-config/ubuntu-config/ansible/group_vars/all.yml

# Re-run setup to regenerate Home Manager configuration
ansible-playbook setup.yml --tags "home-manager"
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

The TestInfra test suite runs in a dedicated Docker service and provides comprehensive validation using Gherkin syntax organized by domains:

- **Domain Testing**: `test_system.py`, `test_development.py`, `test_browser.py`, `test_communication.py`, `test_media.py`, `test_utility.py`
- **Layer Testing**: `test_home_manager.py`, `test_keys.py`
- **Configuration Testing**: `test_configuration.py`, `test_shell.py`

Each test file follows Gherkin scenarios to validate:

- Package installation and configuration
- Service status and functionality
- File permissions and configurations
- User environment setup
- Domain-specific application installations

Tests are triggered on every push to the repository and provide detailed reports on the system configuration status.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to
discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
