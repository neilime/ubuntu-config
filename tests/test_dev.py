"""Tests for development tools setup."""

import pytest

pytestmark = pytest.mark.dev


class TestDocker:
    """Test Docker installation and configuration."""

    def test_docker_installed(self, host):
        """Test that Docker is installed."""
        docker_cmd = host.run("docker --version")
        assert docker_cmd.rc == 0
        assert "Docker" in docker_cmd.stdout

    def test_docker_compose_installed(self, host):
        """Test that Docker Compose is installed."""
        compose_cmd = host.run("docker-compose --version")
        assert compose_cmd.rc == 0
        assert (
            "Docker Compose" in compose_cmd.stdout
            or "docker-compose" in compose_cmd.stdout
        )

    def test_docker_service_running(self, host):
        """Test that Docker service is running."""
        docker_service = host.service("docker")
        assert docker_service.is_running
        assert docker_service.is_enabled

    def test_docker_group_exists(self, host):
        """Test that docker group exists."""
        docker_group = host.group("docker")
        assert docker_group.exists


class TestNodeJS:
    """Test Node.js and related tools installation."""

    def test_nodejs_installed(self, host):
        """Test that Node.js is installed."""
        node_cmd = host.run("node --version")
        assert node_cmd.rc == 0
        assert node_cmd.stdout.strip().startswith("v")

    def test_npm_installed(self, host):
        """Test that npm is installed."""
        npm_cmd = host.run("npm --version")
        assert npm_cmd.rc == 0
        # npm version should be a semantic version
        assert npm_cmd.stdout.strip().replace(".", "").isdigit()

    def test_nvm_installed(self, host, target_user):
        """Test that NVM is installed."""
        # NVM is typically installed in user's home directory
        nvm_cmd = host.run(
            f"sudo -u {target_user} bash -c 'source ~/.nvm/nvm.sh && nvm --version'"
        )
        assert nvm_cmd.rc == 0
        # NVM version should be a semantic version
        assert nvm_cmd.stdout.strip().replace(".", "").isdigit()

    def test_yarn_installed(self, host):
        """Test that Yarn is installed."""
        yarn_cmd = host.run("yarn --version")
        assert yarn_cmd.rc == 0
        # Yarn version should be a semantic version
        assert yarn_cmd.stdout.strip().replace(".", "").isdigit()


class TestPHP:
    """Test PHP and Composer installation."""

    def test_php_installed(self, host):
        """Test that PHP is installed."""
        php_cmd = host.run("php --version")
        assert php_cmd.rc == 0
        assert "PHP" in php_cmd.stdout

    def test_composer_installed(self, host):
        """Test that Composer is installed."""
        composer_cmd = host.run("composer --version")
        assert composer_cmd.rc == 0
        assert "Composer" in composer_cmd.stdout

    def test_php_extensions(self, host):
        """Test that common PHP extensions are available."""
        # Test a few common extensions
        extensions_to_check = ["json", "curl", "mbstring"]

        for extension in extensions_to_check:
            ext_cmd = host.run(f"php -m | grep -i {extension}")
            assert ext_cmd.rc == 0, f"PHP extension {extension} should be available"


class TestGit:
    """Test Git configuration."""

    def test_git_installed(self, host):
        """Test that Git is installed."""
        git_cmd = host.run("git --version")
        assert git_cmd.rc == 0
        assert "git version" in git_cmd.stdout

    def test_git_config_exists(self, host, user_home):
        """Test that Git configuration exists."""
        git_config = host.file(f"{user_home}/.gitconfig")
        if git_config.exists:
            assert git_config.is_file
            # Check for basic configuration
            assert git_config.contains("[user]") or git_config.contains("[core]")


class TestDevelopmentPackages:
    """Test additional development packages."""

    @pytest.mark.parametrize(
        "package",
        [
            "make",
            "curl",
            "wget",
            "unzip",
            "gh",  # GitHub CLI
        ],
    )
    def test_dev_packages_installed(self, host, package):
        """Test that development packages are installed."""
        pkg = host.package(package)
        assert pkg.is_installed, f"Development package {package} should be installed"

    def test_python_dev_tools(self, host):
        """Test Python development tools."""
        python3 = host.package("python3-dev")
        assert python3.is_installed

        pip3 = host.package("python3-pip")
        assert pip3.is_installed

        setuptools = host.package("python3-setuptools")
        assert setuptools.is_installed
