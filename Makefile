.PHONY: help

help: ## Display help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

lint: ## Execute linting
	$(call run_linter,)

lint-fix: ## Execute linting and fix
	$(call run_linter, \
		-e FIX_JSON_PRETTIER=true \
		-e FIX_JAVASCRIPT_PRETTIER=true \
		-e FIX_YAML_PRETTIER=true \
		-e FIX_MARKDOWN=true \
		-e FIX_MARKDOWN_PRETTIER=true \
		-e FIX_NATURAL_LANGUAGE=true \
		-e FIX_SHELL_SHFMT=true \
		-e FIX_PYTHON_RUFF=true \
		-e FIX_PYTHON_BLACK=true \
	)

setup: ## Setup the project stack
	$(MAKE) setup-ssh-keys
	@docker compose up --remove-orphans --build -d

down: ## Stop the project stack
	@docker compose down --rmi all --remove-orphans

.PHONY: ansible
ansible: ## Run ansible
	@docker compose exec ansible /home/ubuntu/.local/bin/ansible $(filter-out $@,$(MAKECMDGOALS))

ansible-playbook: ## Run ansible-playbook
	@docker compose exec ansible /home/ubuntu/.local/bin/ansible-playbook $(filter-out $@,$(MAKECMDGOALS))

ansible-galaxy: ## Run ansible-galaxy
	@docker compose exec ansible /home/ubuntu/.local/bin/ansible-galaxy $(filter-out $@,$(MAKECMDGOALS))

ansible-lint: ## Run ansible-lint
	@docker compose exec ansible /home/ubuntu/.local/bin/ansible-lint $(filter-out $@,$(MAKECMDGOALS))

setup-ssh-keys: ## Setup ssh keys for VM access
	./vm/setup-ssh-keys.sh

define check_lima
	@command -v limactl >/dev/null 2>&1 || { \
		echo "❌ Lima is not installed. Please install Lima to use VM commands."; \
		echo ""; \
		echo "📖 Installation instructions: https://lima-vm.io/docs/installation/"; \
		echo ""; \
		exit 1; \
	}
	@echo "✅ Lima is installed"
	@command -v qemu-img >/dev/null 2>&1 || { \
		echo ""; \
		echo "❌ qemu-img not found. Lima (qemu driver) needs qemu-img to inspect VM disk images."; \
		echo ""; \
		echo "Install on Debian/Ubuntu: sudo apt update && sudo apt install -y qemu-utils"; \
		echo "Install on Fedora: sudo dnf install -y qemu-img"; \
		echo "Install on macOS (Homebrew): brew install qemu"; \
		echo ""; \
		exit 1; \
	}
	@echo "✅ qemu-img found"
	@command -v qemu-system-x86_64 >/dev/null 2>&1 || { \
		echo ""; \
		echo "❌ qemu-system-x86_64 not found. QEMU is required to run VM instances with the qemu driver."; \
		echo ""; \
		echo "Install on Debian/Ubuntu: sudo apt update && sudo apt install -y qemu-system-x86 qemu-kvm"; \
		echo "Install on Fedora: sudo dnf install -y qemu-kvm"; \
		echo "Install on macOS (Homebrew): brew install qemu"; \
		echo ""; \
		exit 1; \
	}
	@echo "✅ qemu-system-x86_64 found"
endef

vm-setup: ## Setup the VM
	$(call check_lima)
	$(MAKE) setup-ssh-keys
	@limactl list ubuntu-config-test 2>/dev/null | grep -q "Running" && \
	echo "VM is already up" || ( \
		echo "Starting Lima VM..." && \
		limactl start --yes --name=ubuntu-config-test vm/lima-ubuntu-desktop.yml \
	)

vm-open: ## Open the VM (remote desktop)
	@echo "Remote desktop not directly supported with Lima. Use 'make vm-shell' to access the VM via SSH."
	@echo "For GUI access, consider using X11 forwarding with 'ssh -X' or VNC setup."

vm-shell: ## Open a shell in the VM
	@limactl shell ubuntu-config-test

vm-restore: ## Restore the VM to initial state
	@echo "Stopping VM and restarting to restore initial state..."
	@limactl stop ubuntu-config-test 2>/dev/null || true
	@limactl delete ubuntu-config-test 2>/dev/null || true
	@echo "VM reset. Use 'make vm-setup' to recreate it."

vm-down: ## Stop the VM
	@limactl list ubuntu-config-test 2>/dev/null | grep -q "ubuntu-config-test" && (limactl stop -f ubuntu-config-test && limactl delete ubuntu-config-test) || echo "VM is already down"

vm-status: ## Show VM status
	@echo "Lima VMs:"
	@limactl list 2>/dev/null || echo "No Lima VMs found"

vm-install-script:  ## Run install script on VM
	@echo "Running install script inside VM..."
	@limactl list ubuntu-config-test 2>/dev/null | grep -q "Running" || (echo "VM not running. Run 'make vm-setup' first." && exit 1)
	@docker compose ps git >/dev/null 2>&1 || (echo "Host docker compose 'git' service not running. Start it with 'make setup' or 'docker compose up -d'" && exit 1)
	@echo "Using .env to provide Bitwarden credentials into the VM (ensure .env is protected)"
	@sh vm/run-install-in-vm.sh

vm-test: ## Test install script result on VM
	@echo "Running TestInfra tests on VM..."
	@docker compose run --rm test python3 tests/run_tests.py --verbose --host="ssh://ubuntu@127.0.0.1:60022" --user="ubuntu"

define run_linter
	DEFAULT_WORKSPACE="$(CURDIR)"; \
	LINTER_IMAGE="linter:latest"; \
	VOLUME="$$DEFAULT_WORKSPACE:$$DEFAULT_WORKSPACE"; \
	docker build --build-arg UID=$(shell id -u) --build-arg GID=$(shell id -g) --tag $$LINTER_IMAGE .; \
	docker run \
		-e DEFAULT_WORKSPACE="$$DEFAULT_WORKSPACE" \
		-e FILTER_REGEX_INCLUDE="$(filter-out $@,$(MAKECMDGOALS))" \
		-e IGNORE_GITIGNORED_FILES=true \
		$(1) \
		-v $$VOLUME \
		--rm \
		$$LINTER_IMAGE
endef

#############################
# Argument fix workaround
#############################
%:
	@: