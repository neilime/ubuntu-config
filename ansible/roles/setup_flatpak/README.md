# Setup Flatpak Role

This Ansible role manages Flatpak applications as part of the desktop layer in our Clean Architecture setup.

## Purpose

Flatpak provides sandboxed applications with better security and dependency management compared to traditional package managers. This role replaces most Snap packages for better performance and wider application availability.

## What it does

1. **Installs Flatpak**: Ensures the Flatpak runtime is installed
2. **Adds Flathub repository**: Configures the primary source for Flatpak applications
3. **Installs applications**: Manages a curated list of desktop applications
4. **Updates packages**: Keeps Flatpak applications up to date

## Default Applications

The role installs these applications by default:

- **com.visualstudio.code**: Visual Studio Code (replaces Snap version)
- **com.slack.Slack**: Slack communication (replaces Snap version)  
- **com.spotify.Client**: Spotify music player (replaces Snap version)
- **org.chromium.Chromium**: Chromium web browser

## Configuration

You can customize the applications list in `group_vars/all.yml`:

```yaml
flatpak_packages:
  - com.visualstudio.code
  - com.slack.Slack
  - com.spotify.Client
  - org.chromium.Chromium
  - org.gimp.GIMP           # Add more applications
  - org.libreoffice.LibreOffice
```

## Usage

### Install Flatpak layer only
```bash
ansible-playbook setup.yml --tags "flatpak"
```

### Install complete desktop layer
```bash
ansible-playbook setup.yml --tags "desktop"
```

## Benefits over Snap

1. **Performance**: Faster startup times and better resource usage
2. **Sandboxing**: Better security isolation
3. **Application availability**: Larger selection of applications
4. **Updates**: More reliable update mechanism
5. **Cross-distribution**: Works consistently across Linux distributions

## Container Compatibility

This role automatically detects when running in a container and skips Flatpak operations that require a full desktop environment.

## Testing

Run the Flatpak-specific tests:

```bash
pytest tests/test_flatpak.py
```

## Migration from Snap

If migrating from Snap packages:

1. **Install Flatpak versions** first using this role
2. **Test functionality** of Flatpak applications
3. **Remove Snap versions** when confident in Flatpak replacements
4. **Update shortcuts and favorites** to point to Flatpak applications

The new configuration includes updated favorites that reference Flatpak application IDs instead of Snap package names.