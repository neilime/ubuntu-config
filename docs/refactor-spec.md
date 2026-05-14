# Ubuntu Config v1 Refactor Spec

- Status: Implemented on `v1`
- Date: 2026-05-14

## Purpose

This document records the target that the `v1` branch is meant to ship, along
with the reasons behind the main architecture and workflow choices.

It is not a future proposal for a different branch. It describes the shape this
branch is expected to keep unless a later change intentionally replaces part of
the design.

The decision order in this spec is intentional:

- the remote install contract for a fresh Ubuntu machine comes first
- the repository as source of truth comes second
- local development and CI choices are only relevant when they protect those
  two outcomes without becoming target-machine requirements

## Final Outcome

The `v1` branch delivers a production-target Ubuntu configuration repository
with these properties:

- one-command local developer setup through `make setup`
- one-command local static analysis through `make lint`
- one-command local lint autofix through `make lint-fix`
- one-command Ansible syntax validation through `make check-ansible`
- one-command end-to-end VM lifecycle through `make e2e-*`
- one-command machine bootstrap through `install.sh`
- one-command remote bootstrap for a fresh Ubuntu machine without a prior
  repository checkout
- the repository is the source of truth for installed libraries, tools,
  software, and configuration
- the same high-level flow locally and in CI

The repository currently manages a deliberately narrow machine state, but the
branch goal is final-state quality for everything it does declare and validate.

## Goals

- Keep host requirements low for normal repository work.
- Keep the public command surface small and explicit.
- Make the repository reproducible locally and in CI.
- Validate real install behavior in an end-to-end VM flow, not only static
  checks.
- Make fresh-machine setup reachable from the repository-owned install script,
  with no manual prerequisite installation beyond the standard Ubuntu base
  system and network access.
- Keep the desired machine state versioned in this repository instead of
  relying on undocumented local setup steps.
- Keep the branch understandable enough to remain maintainable as the shipped
  source of truth.

## Non-Goals

- Do not preserve the previous repository shape just for compatibility.
- Do not require developers to install Python, Ansible, or test tools directly
  on the host.
- Do not require operators to clone the repository or preinstall Ansible before
  a fresh Ubuntu machine can be bootstrapped.
- Do not treat machine-local packages, tools, or configuration as canonical if
  they are not declared in this repository.
- Do not ship repository behavior that is framed as temporary or transitional.

## Final Decisions

The choices below are only considered valid if they strengthen or protect the
final install goal. Repository-maintainer tooling is acceptable when it reduces
drift and validation cost, but it must stay outside the runtime contract of the
fresh machine being installed.

### Ansible Stays the Configuration Engine

Ansible remains the system configuration layer.

Reasons:

- it matches the repository's real job: configuring a machine
- it gives idempotency and a familiar install model
- it supports repository-side validation and remote installation through the same source tree

Current implementation:

- [ansible/setup.yml](/home/emilien/Documents/dev-projects/escemi/ubuntu-config/ansible/setup.yml)
- [ansible/ansible.cfg](/home/emilien/Documents/dev-projects/escemi/ubuntu-config/ansible/ansible.cfg)
- [ansible/inventory.yml](/home/emilien/Documents/dev-projects/escemi/ubuntu-config/ansible/inventory.yml)
- [ansible/collections/ansible_collections/neilime/ubuntu_config/galaxy.yml](/home/emilien/Documents/dev-projects/escemi/ubuntu-config/ansible/collections/ansible_collections/neilime/ubuntu_config/galaxy.yml)

### Remote Install Is a First-Class Contract

The repository-owned install entrypoint must stay capable of bootstrapping a
fresh Ubuntu machine from the network, without requiring a prior repository
checkout.

Reasons:

- the primary product of this repository is machine setup, not just local
  developer tooling
- a fresh-machine install path is required to validate that the repository can
  reproduce its target state from scratch
- local development and CI are only meaningful if the same repository state can
  also drive remote installation
- the default installer behavior should match the remote bootstrap contract,
  not infer a maintainer shortcut from local filesystem state

Current implementation:

- `install.sh` installs bootstrap packages itself when Ansible is missing
- `install.sh` uses `ansible-pull` as its only install path
- `REPOSITORY_URL` and `REPOSITORY_BRANCH` select the remote source that is
  installed
- [install.sh](/home/emilien/Documents/dev-projects/escemi/ubuntu-config/install.sh)

### Direct Docker Runs Replace Compose

Normal repository work uses direct `docker run` calls and does not require
Docker Compose. This is a repository maintenance choice, not part of the target
machine install contract.

Reasons:

- the repository does not need Compose orchestration for its current workflow
- `docker run` is enough for the current workflow
- removing Compose reduces host requirements and moving parts
- this keeps maintainer-side tooling isolated without adding dependencies to the
  Ubuntu machine being installed

Current implementation:

- `make setup` builds or pulls `TOOLING_IMAGE`
- `make tool-shell`, `make check-ansible`, and `make test` run in that image
- lint commands use a separate project-owned Super-Linter image built from the
  repository root Dockerfile
- `TOOLING_IMAGE` selects the tooling image used locally and in CI
- [docker/tooling/Dockerfile](/home/emilien/Documents/dev-projects/escemi/ubuntu-config/docker/tooling/Dockerfile)
- [docker/tooling/requirements.txt](/home/emilien/Documents/dev-projects/escemi/ubuntu-config/docker/tooling/requirements.txt)
- [Dockerfile](/home/emilien/Documents/dev-projects/escemi/ubuntu-config/Dockerfile)
- [Makefile](/home/emilien/Documents/dev-projects/escemi/ubuntu-config/Makefile)

### Super-Linter Is the Chosen Lint Surface

The final `v1` branch keeps Super-Linter as the main lint entrypoint instead of
maintaining a second explicit lint stack in the tooling image. This is a
repository quality-control choice, not part of the target machine runtime.

Reasons:

- it already covers Ansible and shell linting
- duplicating those checks in the tooling image adds maintenance with little
  benefit
- the branch target is one effective lint path, not two partially overlapping
  ones
- one lint surface reduces drift in the repository that defines the install
  state

Current implementation:

- `make lint`
- `make lint-fix`
- `make test` runs `ansible-test sanity` and `ansible-test units` from the
  internal collection source tree
- the root Dockerfile builds the local Super-Linter runner image used by those
  commands
- [Dockerfile](/home/emilien/Documents/dev-projects/escemi/ubuntu-config/Dockerfile)
- [Makefile](/home/emilien/Documents/dev-projects/escemi/ubuntu-config/Makefile)

### Lima Stays the End-to-End VM Runtime

Full install validation uses Lima and QEMU. This choice exists to validate the
fresh-machine install contract before changes ship.

Reasons:

- the project needs a real Ubuntu VM for end-to-end validation
- Docker is appropriate for tooling, not for simulating the host machine
- the VM flow is required locally and in CI

Current implementation:

- `make e2e-up`
- `make e2e-install`
- `make e2e-test`
- `make e2e-down`
- the end-to-end VM uses a release-pinned Ubuntu cloud image and does not preinstall the
  repository bootstrap tooling
- the end-to-end install step fetches `install.sh` over HTTPS, then validates
  the pull-based install path against the selected remote branch or commit
- `make e2e-test` runs a dedicated testinfra suite on the VM after the install
  completes
- [e2e-tests/lima-ubuntu.yml](/home/emilien/Documents/dev-projects/escemi/ubuntu-config/e2e-tests/lima-ubuntu.yml)
- [e2e-tests/e2e-install.sh](/home/emilien/Documents/dev-projects/escemi/ubuntu-config/e2e-tests/e2e-install.sh)
- [e2e-tests/e2e-test.sh](/home/emilien/Documents/dev-projects/escemi/ubuntu-config/e2e-tests/e2e-test.sh)

### CI Reuses the Built Tooling Image

CI builds the tooling image once, then reuses that image for the jobs that need
the repository tooling runtime. This is a repository validation choice, not an
install-time dependency for the target machine.

Reasons:

- local and CI behavior should stay aligned
- the static job should not rebuild the tooling environment differently from the
  build job
- reusable workflows remain acceptable as long as their pinned versions are
  explicit and inspectable
- CI should spend effort validating the install contract, not re-solving the
  same tooling environment in multiple ways

Current implementation:

- the `linter` job is separate from the tooling-image workflow
- the `static` job logs into GHCR, uses the built tooling image, and runs
  `make check-ansible` and `make test`
- the `remote-install` job executes `install.sh` on the runner and performs a
  minimal installed-state smoke check
- the `e2e` job runs `install.sh` and a dedicated testinfra suite on the VM
- [\_\_shared-ci.yml](/home/emilien/Documents/dev-projects/escemi/ubuntu-config/.github/workflows/__shared-ci.yml)
- [pull-request-ci.yml](/home/emilien/Documents/dev-projects/escemi/ubuntu-config/.github/workflows/pull-request-ci.yml)
- [main-ci.yml](/home/emilien/Documents/dev-projects/escemi/ubuntu-config/.github/workflows/main-ci.yml)

### The Repository Is the Source of Truth

This repository is expected to own the declared machine state.

Reasons:

- installed libraries, tools, software, and configuration must be reviewable
  and versioned
- End-to-end validation and CI are only trustworthy when the repository fully
  describes the state they validate
- undocumented local setup creates drift that the project cannot reproduce or
  support

Current implementation:

- the Ansible playbook and inventory live in the repository
- the install entrypoint, tooling images, and CI definitions live in the
  repository
- future additions to the machine state must be introduced through versioned
  repository changes, not manual machine-local setup
- [ansible/setup.yml](/home/emilien/Documents/dev-projects/escemi/ubuntu-config/ansible/setup.yml)
- [install.sh](/home/emilien/Documents/dev-projects/escemi/ubuntu-config/install.sh)
- [docker/tooling/Dockerfile](/home/emilien/Documents/dev-projects/escemi/ubuntu-config/docker/tooling/Dockerfile)
- [Makefile](/home/emilien/Documents/dev-projects/escemi/ubuntu-config/Makefile)
- [\_\_shared-ci.yml](/home/emilien/Documents/dev-projects/escemi/ubuntu-config/.github/workflows/__shared-ci.yml)

## Host Dependency Policy

Maintainer-workstation dependencies and target-machine install dependencies are
intentionally different. Docker, Super-Linter, and Lima support repository
development and validation; they are not part of the contract for the Ubuntu
machine being configured.

Required for normal repository work:

- Docker Engine
- Git
- Make

Required on a fresh target machine for remote install:

- network access
- a standard Ubuntu base system with `sudo`

Required only for end-to-end validation:

- cURL
- Lima
- `qemu-img`
- `qemu-system-x86_64`

Not required on the host:

- Python
- Ansible
- pytest
- ansible-lint
- shellcheck
- yamllint

## Public Commands

The branch is expected to preserve these commands as its public task interface:

- `make setup`
- `make tool-shell`
- `make lint`
- `make lint-fix`
- `make check-ansible`
- `make e2e-up`
- `make e2e-install`
- `make e2e-test`
- `make e2e-down`
- `install.sh`

## Managed State Contract

The current playbook writes managed state markers for system and user scope.
That declared state is intentionally narrow.

Even with that narrow scope, the contract stays the same: managed machine state
must remain reachable through `install.sh` and declared in this repository.

That narrower declared state does not reduce the quality bar. Everything the
repository manages must meet the same fresh-machine remote install contract.

It exists to prove:

- the bootstrap path works
- the Ansible path is wired correctly
- the VM validation path works
- CI can validate the same branch shape

It currently does that with:

- a repository-side Ansible syntax check through `make check-ansible`
- a runner-side remote-install smoke check in CI
- a VM-side testinfra suite through `make e2e-test`

Any future change to the declared machine state must preserve these validation
paths instead of bypassing them.

## Change Rule

Any change on this branch should preserve these invariants unless the
change intentionally updates this spec in the same pull request:

- one clear lint path
- one clear tooling runtime
- one clear install path
- one remote install path for a fresh Ubuntu machine
- one real end-to-end VM path
- one documented CI shape
- one repository-owned source of truth for installed libraries, tools,
  software, and configuration
