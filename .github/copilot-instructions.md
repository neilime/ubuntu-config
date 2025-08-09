# GitHub Copilot Instructions for ubuntu-config

This repository contains Ansible-based Ubuntu configuration and setup automation. Follow these guidelines when working with this codebase to maintain high quality, clean architecture, and production-grade standards.

## Repository Context

This project automates Ubuntu desktop/server setup using:

- **Ansible** for configuration management and automation
- **Docker & Docker Compose** for development and testing environments
- **GitHub Actions** for CI/CD pipelines
- **Multipass** for VM-based testing
- **Make** for build automation and task management

## Clean Code Principles

### General Code Quality

- Write self-documenting code with clear, descriptive names for variables, tasks, and functions
- Keep functions and tasks small and focused on a single responsibility
- Use consistent formatting and follow established conventions
- Remove dead code, unused variables, and commented-out sections
- Prefer explicit configuration over implicit behavior

### Ansible Best Practices

- Use descriptive task names that explain what the task accomplishes
- Group related tasks into logical roles and keep roles focused
- Use `ansible.builtin` collection explicitly for core modules
- Implement idempotency - tasks should be safe to run multiple times
- Use `check_mode` compatible tasks when possible
- Handle errors gracefully with appropriate `failed_when` and `ignore_errors`
- Use `block` and `rescue` for complex error handling
- Tag tasks appropriately for selective execution

### YAML Standards

- Use 2-space indentation consistently
- Quote strings that contain special characters or could be ambiguous
- Use literal (`|`) or folded (`>`) style for multi-line strings
- Keep line length under 120 characters
- Use meaningful comments for complex logic or non-obvious configurations
- Order dictionary keys logically (alphabetically or by importance)

### Shell Script Quality

- Use `set -euo pipefail` for strict error handling
- Quote variables to prevent word splitting: `"$variable"`
- Use `[[` instead of `[` for conditional tests
- Implement proper logging and error messages
- Make scripts idempotent where possible
- Use functions for repeated code blocks

### Docker Best Practices

- Use multi-stage builds to minimize image size
- Implement non-root users for security
- Use specific version tags instead of `latest`
- Minimize layers by combining RUN commands where logical
- Use `.dockerignore` to exclude unnecessary files
- Set appropriate health checks and resource limits

## Clean Architecture Principles

### Configuration Management Architecture

- **Separation of Concerns**: Separate environment-specific configurations from role logic
- **Single Responsibility**: Each Ansible role should have one clear purpose
- **Dependency Inversion**: Use variables and defaults to make roles configurable
- **Interface Segregation**: Create focused, minimal role interfaces
- **Open/Closed Principle**: Design roles to be extensible without modification

### Project Structure

- Keep roles atomic and reusable across different environments
- Use `group_vars` and `host_vars` for environment-specific configurations
- Implement proper dependency management between roles
- Use inventory groups logically to represent infrastructure patterns
- Separate secrets management from configuration logic

### Data Flow

- Configuration flows from inventory → group_vars → host_vars → role defaults → role vars
- Avoid circular dependencies between roles
- Use clear naming conventions for variable scopes
- Document variable precedence and expected inputs/outputs

## Technology Standards

### Version Management

- Pin Ansible collections to specific versions in `requirements.yml`
- Use semantic versioning for any custom modules or plugins
- Keep base images and tools updated to latest stable versions
- Document version compatibility in readme and role documentation
- Use Renovate/Dependabot for automated dependency updates

### Production-Grade Requirements

- All roles must support `check_mode` for dry-run capabilities
- Implement comprehensive logging and debugging options
- Use encrypted storage for sensitive data (Ansible Vault, external secrets)
- Support both Ubuntu LTS versions currently in support
- Test on multiple architectures if applicable (x86_64, ARM64)
- Implement rollback strategies for critical changes

### Security Practices

- Never commit secrets or sensitive data to the repository
- Use Ansible Vault for encrypted variables when needed
- Implement least privilege principles in user and service configurations
- Validate and sanitize external inputs
- Use official, trusted sources for packages and downloads
- Implement proper file permissions and ownership

## CI/CD Compliance

### Pre-commit Requirements

- All code must pass linting checks defined in `.github/workflows/`
- Ansible syntax validation must pass (`ansible-playbook --syntax-check`)
- YAML linting must pass (yamllint)
- Markdown linting must pass for documentation
- Shell scripts must pass shellcheck

### Testing Standards

- New roles must include molecule tests or equivalent
- Changes to existing roles must not break existing tests
- Test both successful execution and proper error handling
- Include tests for different Ubuntu versions where applicable
- Verify idempotency in test scenarios

### Documentation Requirements

- Update readme.md for any significant feature changes
- Document new variables in role documentation
- Include examples for complex configurations
- Update installation instructions if setup process changes
- Maintain changelog for breaking changes

## Code Review Standards

### Pull Request Requirements

- Include clear description of changes and motivation
- Reference relevant issues using "Fixes #123" or "Relates to #123"
- Include test evidence (screenshots, logs) for significant changes
- Update documentation alongside code changes
- Ensure all CI checks pass before requesting review

### Review Checklist

- Verify adherence to clean code principles
- Check for proper error handling and logging
- Validate security implications of changes
- Ensure backward compatibility or document breaking changes
- Confirm test coverage for new functionality

## Repository-Specific Guidelines

### File Organization

- Place new roles in `ansible/roles/` with descriptive names
- Use `ansible/group_vars/` for environment-specific configurations
- Add new workflows to `.github/workflows/` following existing patterns
- Update `.github/dependabot.yml` for new dependency sources

### Naming Conventions

- Roles: `kebab-case` (e.g., `git-config`, `zsh-setup`)
- Variables: `snake_case` with role prefix (e.g., `git_config_user_name`)
- Tasks: Descriptive sentences starting with action verb
- Files: Follow directory-specific conventions (see existing examples)

### Performance Considerations

- Minimize network requests in Ansible tasks
- Use package manager batch operations when possible
- Implement caching strategies for downloaded content
- Consider task execution time in design decisions
- Use `async` for long-running tasks when appropriate

### Maintenance Guidelines

- Keep roles focused and avoid feature creep
- Regular dependency updates through automated PRs
- Monitor for deprecated Ansible modules and update accordingly
- Maintain compatibility with supported Ubuntu LTS versions
- Archive or remove unused roles and configurations

## Emergency Procedures

### Rollback Strategy

- All configuration changes should be reversible
- Document rollback procedures for critical system changes
- Test rollback procedures during development
- Maintain previous configuration state information

### Troubleshooting

- Include debug tasks that can be enabled via variables
- Implement comprehensive logging for troubleshooting
- Document common issues and solutions in role documentation
- Provide clear error messages with actionable guidance

---

Remember: The goal is to create maintainable, reliable, and secure Ubuntu configurations that can be easily understood, modified, and extended by team members.
