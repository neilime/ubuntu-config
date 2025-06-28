#!/usr/bin/env bash

# Lima E2E Test Runner
# This script manages Lima VMs for ubuntu-config testing

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
LIMA_CONFIG_DIR="$SCRIPT_DIR/../lima"

# Default values
VM_NAME="ubuntu-config-test"
CONFIG_TYPE="server"  # server or desktop
DESTROY_AFTER_TEST=false
SKIP_PROVISIONING=false
TEST_TIMEOUT=1800  # 30 minutes

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

# Usage information
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

OPTIONS:
    -n, --name NAME         VM name (default: ubuntu-config-test)
    -t, --type TYPE         Config type: server or desktop (default: server)
    -d, --destroy           Destroy VM after test completion
    -s, --skip-provision    Skip provisioning if VM already exists
    -T, --timeout SECONDS  Test timeout in seconds (default: 1800)
    -h, --help              Show this help message

EXAMPLES:
    # Run server tests (default)
    $0

    # Run desktop tests with custom name
    $0 --type desktop --name my-desktop-test

    # Run tests and cleanup afterwards
    $0 --destroy

    # Quick test on existing VM
    $0 --skip-provision --name existing-vm
EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -n|--name)
                VM_NAME="$2"
                shift 2
                ;;
            -t|--type)
                CONFIG_TYPE="$2"
                shift 2
                ;;
            -d|--destroy)
                DESTROY_AFTER_TEST=true
                shift
                ;;
            -s|--skip-provision)
                SKIP_PROVISIONING=true
                shift
                ;;
            -T|--timeout)
                TEST_TIMEOUT="$2"
                shift 2
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    # Validate config type
    if [[ "$CONFIG_TYPE" != "server" && "$CONFIG_TYPE" != "desktop" ]]; then
        error "Invalid config type: $CONFIG_TYPE. Must be 'server' or 'desktop'"
        exit 1
    fi
}

# Check if Lima is available
check_lima() {
    if ! command -v limactl &> /dev/null; then
        error "Lima is not installed. Run scripts/lima-setup.sh first."
        exit 1
    fi
}

# Get the appropriate config file
get_config_file() {
    case "$CONFIG_TYPE" in
        "server")
            echo "$LIMA_CONFIG_DIR/ubuntu-server-ci.yaml"
            ;;
        "desktop")
            echo "$LIMA_CONFIG_DIR/ubuntu-desktop.yaml"
            ;;
    esac
}

# Check if VM exists
vm_exists() {
    limactl list | grep -q "^$VM_NAME " || false
}

# Check if VM is running
vm_running() {
    limactl list | grep "^$VM_NAME " | grep -q "Running" || false
}

# Create and start VM
create_vm() {
    local config_file
    config_file=$(get_config_file)
    
    if ! [[ -f "$config_file" ]]; then
        error "Configuration file not found: $config_file"
        exit 1
    fi
    
    info "Creating Lima VM: $VM_NAME (type: $CONFIG_TYPE)"
    info "Using config: $(basename "$config_file")"
    
    if vm_exists && ! $SKIP_PROVISIONING; then
        warn "VM '$VM_NAME' already exists. Deleting and recreating..."
        limactl delete --force "$VM_NAME" || true
    fi
    
    if ! vm_exists; then
        # Set environment variables for the VM
        export REPOSITORY_URL=${REPOSITORY_URL:-https://github.com/neilime/ubuntu-config.git}
        export REPOSITORY_BRANCH=${REPOSITORY_BRANCH:-main}
        
        info "Creating VM with repository: $REPOSITORY_URL (branch: $REPOSITORY_BRANCH)"
        
        if ! limactl start --name="$VM_NAME" "$config_file"; then
            error "Failed to create VM"
            exit 1
        fi
        
        success "VM created and started: $VM_NAME"
    else
        info "VM '$VM_NAME' already exists, starting if not running..."
        if ! vm_running; then
            limactl start "$VM_NAME"
        fi
        success "VM is running: $VM_NAME"
    fi
}

# Wait for VM to be ready
wait_for_vm() {
    info "Waiting for VM to be ready..."
    
    local max_attempts=60
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if limactl shell "$VM_NAME" test -f /home/ubuntu/run-ubuntu-config-test.sh; then
            success "VM is ready for testing"
            return 0
        fi
        
        ((attempt++))
        info "Waiting for VM setup... (attempt $attempt/$max_attempts)"
        sleep 5
    done
    
    error "VM failed to become ready within expected time"
    return 1
}

# Run tests in the VM
run_tests() {
    info "Running ubuntu-config tests in VM: $VM_NAME"
    
    # Clear previous test results
    limactl shell "$VM_NAME" rm -f /tmp/test-results/e2e-success || true
    
    # Set environment variables for the test
    export REPOSITORY_URL=${REPOSITORY_URL:-https://github.com/neilime/ubuntu-config.git}
    export REPOSITORY_BRANCH=${REPOSITORY_BRANCH:-main}
    
    # Run the test with timeout
    info "Test timeout: ${TEST_TIMEOUT}s"
    info "Repository: $REPOSITORY_URL"
    info "Branch: $REPOSITORY_BRANCH"
    
    if timeout "$TEST_TIMEOUT" limactl shell "$VM_NAME" env \
        REPOSITORY_URL="$REPOSITORY_URL" \
        REPOSITORY_BRANCH="$REPOSITORY_BRANCH" \
        ~/run-ubuntu-config-test.sh; then
        
        # Check if test actually succeeded
        if limactl shell "$VM_NAME" test -f /tmp/test-results/e2e-success; then
            success "Ubuntu-config tests passed!"
            return 0
        else
            error "Test script completed but success marker not found"
            return 1
        fi
    else
        error "Tests failed or timed out"
        return 1
    fi
}

# Collect test results and logs
collect_results() {
    info "Collecting test results..."
    
    local results_dir="/tmp/lima-test-results/$(date +%Y%m%d_%H%M%S)_${VM_NAME}"
    mkdir -p "$results_dir"
    
    # Copy test results from VM
    limactl copy "$VM_NAME":/tmp/test-results/* "$results_dir/" 2>/dev/null || warn "No test results to collect"
    
    # Collect system information
    {
        echo "=== VM Information ==="
        limactl list | grep "^$VM_NAME "
        echo
        echo "=== System Information ==="
        limactl shell "$VM_NAME" uname -a
        echo
        echo "=== Memory Usage ==="
        limactl shell "$VM_NAME" free -h
        echo
        echo "=== Disk Usage ==="
        limactl shell "$VM_NAME" df -h
    } > "$results_dir/system-info.txt"
    
    success "Test results collected in: $results_dir"
}

# Cleanup VM if requested
cleanup_vm() {
    if $DESTROY_AFTER_TEST; then
        info "Cleaning up VM: $VM_NAME"
        limactl delete --force "$VM_NAME" || warn "Failed to delete VM"
        success "VM cleanup completed"
    else
        info "VM '$VM_NAME' is still running. Use 'limactl delete $VM_NAME' to remove it."
    fi
}

# Main execution
main() {
    local exit_code=0
    
    echo "🧪 Lima E2E Test Runner for ubuntu-config"
    echo "========================================="
    echo
    
    parse_args "$@"
    check_lima
    
    info "Configuration:"
    info "  VM Name: $VM_NAME"
    info "  Config Type: $CONFIG_TYPE"
    info "  Config File: $(basename "$(get_config_file)")"
    info "  Destroy After Test: $DESTROY_AFTER_TEST"
    info "  Skip Provisioning: $SKIP_PROVISIONING"
    info "  Test Timeout: ${TEST_TIMEOUT}s"
    echo
    
    # Trap to ensure cleanup on exit
    trap 'collect_results; cleanup_vm' EXIT
    
    create_vm
    wait_for_vm
    
    if run_tests; then
        success "All tests passed! 🎉"
        exit_code=0
    else
        error "Tests failed! 💥"
        exit_code=1
    fi
    
    exit $exit_code
}

# Run main function
main "$@"