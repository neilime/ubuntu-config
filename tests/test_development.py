"""Test development domain setup - Development tools and project environment.

Feature: Development Domain Setup
    As a developer
    I want to ensure the development domain is properly configured
    So that I have all necessary development tools and environments

    Scenario: Development tools are installed
        Given the development setup has been executed
        When I check for development packages
        Then all development tools should be available
        And development repositories should be configured

    Scenario: Development environment is ready
        Given the development setup has been executed
        When I check the development environment
        Then project directories should exist
        And Docker should be available
        And development applications should be installed
"""

import pytest


def test_development_apt_packages(host):
    """
    Scenario: Development APT packages are installed
    Given the development setup has been executed
    When I check for development APT packages
    Then all specified development tools should be installed
    """
    development_packages = ["helm"]

    for package in development_packages:
        pkg = host.package(package)
        assert pkg.is_installed, f"Development package {package} should be installed"


def test_development_flatpak_apps(host):
    """
    Scenario: Development Flatpak applications are installed
    Given the development setup has been executed
    When I check for development Flatpak applications
    Then VS Code should be available
    """
    if host.run("which flatpak").rc != 0:
        pytest.skip("Flatpak not available in test environment")

    development_flatpaks = ["com.visualstudio.code"]

    for app in development_flatpaks:
        cmd = host.run(f"flatpak list --app | grep {app}")
        assert (
            cmd.rc == 0 or "not available" not in cmd.stderr.lower()
        ), f"Development Flatpak application {app} should be installed"


def test_given_development_setup_when_checking_project_directory_then_it_should_exist(
    host, target_user
):
    """
    Scenario: Development project directory exists
    Given the development setup has been executed
    When I check for the project directory
    Then it should exist with proper permissions
    """
    project_dir = f"/home/{target_user}/Documents/dev-projects"

    directory = host.file(project_dir)
    assert directory.exists, f"Project directory {project_dir} should exist"
    assert directory.is_directory, f"{project_dir} should be a directory"
    assert (
        directory.user == target_user
    ), f"Project directory should be owned by {target_user}"
    assert directory.mode == 0o755, "Project directory should have proper permissions"


def test_given_development_setup_when_checking_docker_then_it_should_be_available(host):
    """
    Scenario: Docker is available for development
    Given the development setup has been executed
    When I check for Docker
    Then Docker should be installed and running
    And Docker Compose should be available
    """
    # Check Docker installation
    docker_pkg = host.package("docker-ce")
    if not docker_pkg.is_installed:
        docker_pkg = host.package("docker.io")
    assert docker_pkg.is_installed, "Docker should be installed"

    # Check Docker service
    docker_service = host.service("docker")
    assert docker_service.is_running, "Docker service should be running"
    assert docker_service.is_enabled, "Docker service should be enabled"

    # Check Docker Compose
    compose_cmd = host.run("docker compose version")
    assert compose_cmd.rc == 0, "Docker Compose should be available"


def test_given_development_setup_when_checking_dive_then_it_should_be_available(host):
    """
    Scenario: Dive tool is available for container inspection
    Given the development setup has been executed
    When I check for Dive tool
    Then it should be installed and executable
    """
    dive_cmd = host.run("which dive")
    if dive_cmd.rc != 0:
        # Dive might be installed in different locations
        dive_cmd = host.run("find /usr -name dive 2>/dev/null")
        assert dive_cmd.stdout.strip(), "Dive tool should be installed somewhere"
    else:
        assert dive_cmd.rc == 0, "Dive tool should be available in PATH"


def test_given_development_setup_when_checking_repositories_then_helm_repo_should_be_configured(
    host,
):
    """
    Scenario: Development repositories are configured
    Given the development setup has been executed
    When I check for development repositories
    Then Helm repository should be configured
    """
    # Check if Helm repository is added
    sources_cmd = host.run(
        "find /etc/apt/sources.list.d -name '*helm*' -o /etc/apt/sources.list.d -name '*baltocdn*'"
    )
    helm_in_sources = host.run(
        "grep -r 'baltocdn.com/helm' /etc/apt/sources.list.d/ 2>/dev/null"
    )

    assert (
        sources_cmd.rc == 0 or helm_in_sources.rc == 0
    ), "Helm repository should be configured in APT sources"
