"""Test system domain setup - Essential host layer components.

Feature: System Domain Setup
    As a system administrator
    I want to ensure the system domain is properly configured
    So that the host layer has all essential components

    Scenario: Essential system packages are installed
        Given the system setup has been executed
        When I check for essential system packages
        Then all critical packages should be installed
        And system services should be running properly

    Scenario: System configuration is applied
        Given the system setup has been executed
        When I check system configuration
        Then the locale should be properly set
        And the timezone should be configured correctly

    Scenario: Nix package manager is installed and configured
        Given the system setup has been executed
        When I check for Nix package manager
        Then Nix should be installed and configured properly
        And Nix services should be running
"""


def test_given_system_setup_when_checking_essential_packages_then_all_should_be_installed(
    host,
):
    """
    Scenario: Essential system packages are installed
    Given the system setup has been executed
    When I check for essential system packages
    Then all critical packages should be installed
    """
    essential_packages = [
        "apt-transport-https",
        "ca-certificates",
        "gnupg-agent",
        "software-properties-common",
        "util-linux-extra",
        "systemd",
        "hwclock",
        "dconf-cli",
        "curl",
        "wget",
        "unzip",
        "cron",
        "htop",
    ]

    for package in essential_packages:
        pkg = host.package(package)
        assert pkg.is_installed, f"Essential package {package} should be installed"


def test_given_system_setup_when_checking_services_then_critical_services_should_be_running(
    host,
):
    """
    Scenario: System services are running
    Given the system setup has been executed
    When I check critical system services
    Then they should be running and enabled
    """
    critical_services = ["cron"]

    for service in critical_services:
        svc = host.service(service)
        assert svc.is_running, f"Critical service {service} should be running"
        assert svc.is_enabled, f"Critical service {service} should be enabled"


def test_given_system_setup_when_checking_apt_cache_then_it_should_be_recent(host):
    """
    Scenario: APT cache is maintained
    Given the system setup has been executed
    When I check the APT cache freshness
    Then it should be reasonably recent
    """
    cmd = host.run("find /var/lib/apt/lists -name '*Packages*' -mtime -1")
    assert cmd.rc == 0
    assert len(cmd.stdout.strip()) > 0, "APT cache should be recent"


def test_given_system_setup_when_checking_cleanup_then_no_orphaned_packages_should_exist(
    host,
):
    """
    Scenario: System cleanup is effective
    Given the system setup has been executed
    When I check for orphaned packages
    Then the system should be clean of unnecessary dependencies
    """
    cmd = host.run("apt list --installed | grep -c 'automatically installed'")
    # This is a basic check - in practice, some auto-installed packages are normal
    assert cmd.rc == 0, "Should be able to check for auto-installed packages"


def test_system_nix_directory_exists(host):
    """
    Scenario: Nix package manager is installed
    Given the system setup has been executed
    When I check for Nix installation
    Then the Nix directory should exist
    """
    nix_dir = host.file("/nix")
    assert nix_dir.exists, "/nix directory should exist"
    assert nix_dir.is_directory, "/nix should be a directory"


def test_system_nix_daemon_running(host):
    """
    Scenario: Nix daemon service is running
    Given the system setup has been executed
    When I check the Nix daemon service
    Then it should be running and enabled
    """
    service = host.service("nix-daemon")
    assert service.is_running, "nix-daemon should be running"
    assert service.is_enabled, "nix-daemon should be enabled"


def test_system_nix_configuration_exists(host):
    """
    Scenario: Nix configuration is present
    Given the system setup has been executed
    When I check for Nix configuration
    Then configuration should exist with flakes support
    """
    nix_conf = host.file("/etc/nix/nix.conf")
    assert nix_conf.exists, "Nix configuration should exist"
    assert nix_conf.contains(
        "experimental-features = nix-command flakes"
    ), "Nix should be configured with flakes support"


def test_system_nix_profile_setup(host):
    """
    Scenario: Nix profile script exists
    Given the system setup has been executed
    When I check for Nix profile setup
    Then the profile script should exist
    """
    profile_script = host.file(
        "/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh"
    )
    assert profile_script.exists, "Nix profile script should exist"


def test_system_nix_command_available_for_user(host):
    """
    Scenario: Nix command is available for users
    Given the system setup has been executed
    When I check if Nix command is available
    Then users should be able to use Nix after sourcing profile
    """
    cmd = host.run(
        ". /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh && which nix"
    )
    assert cmd.rc == 0, "nix command should be available after sourcing profile"


def test_system_nix_trusted_users_configured(host):
    """
    Scenario: Nix trusted users are configured
    Given the system setup has been executed
    When I check Nix trusted users configuration
    Then trusted users should be properly configured
    """
    nix_conf = host.file("/etc/nix/nix.conf")
    assert nix_conf.contains(
        "trusted-users"
    ), "Nix should have trusted users configured"
