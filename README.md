# ubuntu-config

Ubuntu machine setup driven entirely from this repository.

The repository is the source of truth for the tools, packages, and machine
configuration applied during installation.

## Install

Fresh Ubuntu machine bootstrap requires only:

- internet access
- `sudo`

Run the public installer:

```sh
curl -fsSL https://raw.githubusercontent.com/neilime/ubuntu-config/main/install.sh | sh
```

The installer bootstraps its own dependencies, then applies the repository with
`ansible-pull`.

To install another branch, tag, or commit explicitly:

```sh
curl -fsSL https://raw.githubusercontent.com/neilime/ubuntu-config/main/install.sh | env REPOSITORY_BRANCH=my-branch sh
```

You can also point the installer at another repository source:

```sh
curl -fsSL https://raw.githubusercontent.com/neilime/ubuntu-config/main/install.sh | env REPOSITORY_URL=https://github.com/your-org/ubuntu-config.git REPOSITORY_BRANCH=my-branch sh
```

## Development

### Host Requirements

Required for normal repository work:

- Docker Engine
- Git
- Make

Required only for end-to-end validation:

- cURL
- Lima
- `qemu-img`
- `qemu-system-x86_64`

### Quick Start

```sh
make setup
make lint
make check-ansible
make test
```

### Static Validation

Repository-side validation is split into three layers:

- `make lint` runs the repository lint surface
- `make check-ansible` runs playbook syntax validation
- `make test` runs `ansible-test sanity` and `ansible-test units`

### End-to-End Validation

The end-to-end flow runs a real user-install-like process inside an Ubuntu VM.
It fetches `install.sh` over HTTPS, executes the same remote-install path that a
user runs, then verifies the resulting machine state with testinfra.

```sh
make e2e-up
make e2e-install
make e2e-test
make e2e-down
```

### CI

CI uses the same repository entry points as local development:

- `make setup`
- `make lint`
- `make check-ansible`
- `make test`
- `make e2e-up`
- `make e2e-install`
- `make e2e-test`

The static and end-to-end layers stay separate in CI as well:

- static checks cover linting, Ansible syntax validation, and `ansible-test`
- end-to-end validation covers the remote install path and VM-level assertions
