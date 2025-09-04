# Setup Nix Role

This Ansible role installs and configures the Nix package manager as the foundation for the project layer in our Clean Architecture setup.

## Purpose

Nix provides reproducible, isolated development environments on a per-project basis. This eliminates "works on my machine" issues and allows developers to have different versions of tools for different projects.

## What it does

1. **Installs Nix**: Multi-user installation with daemon support
2. **Enables flakes**: Configures experimental features (nix-command, flakes)
3. **Sets up daemon**: Ensures nix-daemon service is running and enabled
4. **Configures trusted users**: Allows the current user to manage Nix packages
5. **Cleans up**: Removes temporary installation files

## Configuration

The role creates `/etc/nix/nix.conf` with:

```
experimental-features = nix-command flakes
trusted-users = root <current-user>
```

## Usage

### Install Nix only
```bash
ansible-playbook setup.yml --tags "nix"
```

### Install complete project layer
```bash
ansible-playbook setup.yml --tags "project"
```

## After Installation

Once Nix is installed, you can:

### Use Nix commands
```bash
# Source the Nix profile (automatic in new shells)
. /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh

# Install packages temporarily
nix shell nixpkgs#nodejs nixpkgs#python3

# Create project environments with flakes
nix develop
```

### Create project-specific environments
```bash
# Copy the project template
cp -r ~/Documents/project-template/* /path/to/project/
cd /path/to/project

# Customize flake.nix for your needs
vim flake.nix

# Enter the development environment
nix develop
# OR use direnv for automatic activation
direnv allow
```

## Project Layer Benefits

1. **Reproducibility**: Exact same environment across machines
2. **Isolation**: Projects don't interfere with each other
3. **Rollback**: Easy to revert to previous environment states
4. **Multiple versions**: Different Node.js/Python versions per project
5. **Collaboration**: Share exact development environments via flake.lock

## Example Project Environments

### Node.js Project
```nix
{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  outputs = { nixpkgs, ... }: {
    devShells.x86_64-linux.default = nixpkgs.legacyPackages.x86_64-linux.mkShell {
      buildInputs = with nixpkgs.legacyPackages.x86_64-linux; [
        nodejs_18
        yarn
        nodePackages.typescript
      ];
    };
  };
}
```

### Python Project
```nix
{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  outputs = { nixpkgs, ... }: {
    devShells.x86_64-linux.default = nixpkgs.legacyPackages.x86_64-linux.mkShell {
      buildInputs = with nixpkgs.legacyPackages.x86_64-linux; [
        python310
        python310Packages.pip
        python310Packages.virtualenv
      ];
    };
  };
}
```

## Container Compatibility

This role works in containers but requires:
- Systemd support for the nix-daemon service
- Sufficient privileges for multi-user installation

## Testing

Run the Nix-specific tests:

```bash
pytest tests/test_nix.py
```

## Integration with Home Manager

This role provides the foundation for Home Manager (user layer), which requires Nix to be installed first. The installation order is:

1. **setup_nix** (this role) - Project layer foundation
2. **setup_home_manager** - User layer configuration management