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
endef

docker-install-script: ## Run install script in Docker container
	@echo "Running install script in Docker container..."
	@docker compose exec \
		$(filter-out $@,$(MAKECMDGOALS)) \
		--user kasm-user ubuntu \
		sh -c 'wget -qO- "http://git/?p=ubuntu-config.git;a=blob_plain;f=install.sh;hb=HEAD" | sh'

docker-test: ## Test install script result in Docker container
	@echo "Running TestInfra tests against Docker container..."
	@docker compose exec test \
		python3 tests/run_tests.py --verbose --host="docker://ubuntu" --user="kasm-user"

vm-setup: ## Setup the VM
	$(call check_lima)
	$(MAKE) setup-ssh-keys
	@limactl list ubuntu-config-test 2>/dev/null | grep -q "Running" && \
	echo "VM is already up" || ( \
		echo "Starting Lima VM..." && \
		limactl start --name=ubuntu-config-test vm/lima-ubuntu-desktop.yml \
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
	@limactl list ubuntu-config-test 2>/dev/null | grep -q "ubuntu-config-test" && (limactl stop ubuntu-config-test && limactl delete ubuntu-config-test) || echo "VM is already down"

vm-status: ## Show VM status
	@echo "Lima VMs:"
	@limactl list 2>/dev/null || echo "No Lima VMs found"

vm-install-script:  ## Run install script on VM
	@echo "Running Ansible playbook on VM..."
	docker compose exec ansible sh -c '/root/.local/bin/ansible-playbook setup.yml \
		--limit ubuntu-config-test \
		-e ANSIBLE_HOST=127.0.0.1 \
		-e ansible_port=60022 \
		-e ansible_user=ubuntu \
		-e ansible_ssh_private_key_file=/workspace/vm/id_rsa \
		--diff \
		$(filter-out $@,$(MAKECMDGOALS)) \
	'

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