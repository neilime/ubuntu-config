#!/usr/bin/env bash

# Lima E2E Testing Setup Script
# This script sets up Lima for local ubuntu-config testing

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
LIMA_CONFIG_DIR="$SCRIPT_DIR/../lima"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
info() {
    echo -e "${BLUE}ℹ${NC} $*"
}

success() {
    echo -e "${GREEN}✅${NC} $*"
}

warn() {
    echo -e "${YELLOW}⚠${NC} $*"
}

error() {
    echo -e "${RED}❌${NC} $*" >&2
}

# Check if Lima is installed
check_lima_installation() {
    info "Checking Lima installation..."
    
    if ! command -v limactl &> /dev/null; then
        error "Lima is not installed. Please install Lima first."
        echo
        echo "Installation instructions:"
        echo "  macOS:   brew install lima"
        echo "  Linux:   https://lima-vm.io/docs/installation/"
        echo
        exit 1
    fi
    
    success "Lima is installed: $(limactl --version)"
}

# Check system requirements
check_requirements() {
    info "Checking system requirements..."
    
    # Check if we're on a supported platform
    case "$OSTYPE" in
        darwin*)
            success "Running on macOS - Lima fully supported"
            ;;
        linux*)
            success "Running on Linux - Lima supported"
            # Check for KVM support on Linux
            if [[ -e /dev/kvm ]]; then
                success "KVM acceleration available"
            else
                warn "KVM acceleration not available - VMs will be slower"
            fi
            ;;
        *)
            warn "Running on $OSTYPE - Lima support may be limited"
            ;;
    esac
    
    # Check available resources
    if command -v free &> /dev/null; then
        local total_mem=$(free -g | awk '/^Mem:/{print $2}')
        if [[ $total_mem -lt 8 ]]; then
            warn "Less than 8GB RAM available - consider using ubuntu-server-ci.yaml instead of ubuntu-desktop.yaml"
        else
            success "Sufficient RAM available: ${total_mem}GB"
        fi
    fi
}

# Create test results directory
setup_test_directory() {
    info "Setting up test directories..."
    
    mkdir -p /tmp/lima-test-results
    success "Test results directory created: /tmp/lima-test-results"
}

# Validate Lima configurations
validate_configs() {
    info "Validating Lima configurations..."
    
    for config in "$LIMA_CONFIG_DIR"/*.yaml; do
        if [[ -f "$config" ]]; then
            local config_name=$(basename "$config")
            info "Validating $config_name..."
            
            # Basic YAML syntax check
            if command -v yamllint &> /dev/null; then
                if yamllint "$config" &> /dev/null; then
                    success "$config_name syntax is valid"
                else
                    warn "$config_name has YAML syntax warnings (this may be normal)"
                fi
            else
                info "yamllint not available, skipping syntax validation"
            fi
        fi
    done
}

# Display available configurations
show_configurations() {
    echo
    info "Available Lima configurations:"
    echo
    
    for config in "$LIMA_CONFIG_DIR"/*.yaml; do
        if [[ -f "$config" ]]; then
            local config_name=$(basename "$config" .yaml)
            local config_file=$(basename "$config")
            
            echo "  📁 $config_name"
            echo "     File: $config_file"
            
            # Extract some key info from the config
            if command -v yq &> /dev/null; then
                local cpus=$(yq eval '.cpus' "$config" 2>/dev/null || echo "N/A")
                local memory=$(yq eval '.memory' "$config" 2>/dev/null || echo "N/A")
                local disk=$(yq eval '.disk' "$config" 2>/dev/null || echo "N/A")
                echo "     Resources: ${cpus} CPUs, ${memory} RAM, ${disk} disk"
            fi
            echo
        fi
    done
    
    echo "Usage examples:"
    echo "  # Start Ubuntu Desktop VM for GUI testing:"
    echo "  limactl start --name=ubuntu-config-desktop $LIMA_CONFIG_DIR/ubuntu-desktop.yaml"
    echo
    echo "  # Start Ubuntu Server VM for CI-like testing:"
    echo "  limactl start --name=ubuntu-config-server $LIMA_CONFIG_DIR/ubuntu-server-ci.yaml"
    echo
    echo "  # Run tests in the VM:"
    echo "  limactl shell ubuntu-config-desktop ~/run-ubuntu-config-test.sh"
    echo
}

# Main execution
main() {
    echo "🚀 Lima E2E Testing Setup for ubuntu-config"
    echo "============================================="
    echo
    
    check_lima_installation
    check_requirements
    setup_test_directory
    validate_configs
    show_configurations
    
    success "Lima setup completed successfully!"
    echo
    info "Next steps:"
    echo "  1. Choose a Lima configuration (desktop or server)"
    echo "  2. Create and start a Lima VM"
    echo "  3. Run the ubuntu-config tests inside the VM"
    echo
    info "See the Lima documentation for detailed usage instructions."
}

# Run main function
main "$@"