.PHONY: help

help: ## Display help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

lint: ## Execute linting
	$(call run_linter,)

lint-fix: ## Execute linting and fix
	$(call run_linter, \
		-e IGNORE_GITIGNORED_FILES=true \
		-e FIX_ANSIBLE=true \
		-e FIX_ENV=true \
		-e FIX_JSON_PRETTIER=true \
		-e FIX_JAVASCRIPT_PRETTIER=true \
		-e FIX_JAVASCRIPT_STANDARD=true \
		-e FIX_YAML_PRETTIER=true \
		-e FIX_MARKDOWN=true \
		-e FIX_MARKDOWN_PRETTIER=true \
		-e FIX_NATURAL_LANGUAGE=true\
		-e FIX_SHELL_SHFMT=true \
	)

setup: ## Setup the project stack
	$(MAKE) setup-ssh-keys
	@docker-compose up --remove-orphans --build -d

down: ## Stop the project stack
	@docker-compose down --rmi all --remove-orphans

ansible: ## Run ansible
	@docker-compose exec ansible ansible $(filter-out $@,$(MAKECMDGOALS))

ansible-playbook: ## Run ansible-playbook
	@docker-compose exec ansible ansible-playbook $(filter-out $@,$(MAKECMDGOALS))

ansible-galaxy: ## Run ansible-galaxy
	@docker-compose exec ansible ansible-galaxy $(filter-out $@,$(MAKECMDGOALS))

setup-ssh-keys: ## Setup ssh keys for VM access
	./cloud-init/setup-ssh-keys.sh

setup-vm: ## Setup the VM
	$(MAKE) setup-ssh-keys
	@multipass list --format json | jq -e '.list[] | select(.name == "ubuntu-config-test" and .state == "Running")' && \
	echo "VM is already up" || ( \
		SSH_PUBLIC_KEY=$$(cat cloud-init/id_rsa.pub) && cat cloud-init/user-data.yml | sed "s#{{ ssh_public_key }}#$$SSH_PUBLIC_KEY#g" | \
		multipass launch lts --name ubuntu-config-test --cpus 4 --disk 15G --memory 4G --timeout 3600 --cloud-init - && \
		multipass stop ubuntu-config-test && \
		multipass snapshot ubuntu-config-test --name "initial-setup" && \
		multipass start ubuntu-config-test \
	)

open-vm: ## Open the VM
	@remmina -c rdp:$(shell multipass info ubuntu-config-test | grep IPv4 | awk '{print $$2}')

shell-vm: ## Open a shell in the VM
	@ssh -X -i cloud-init/id_rsa ubuntu@$(shell multipass info ubuntu-config-test | grep IPv4 | awk '{print $$2}')

restore-vm: ## Restore the VM
	@multipass list --format json | jq -e '.list[] | select(.name == "ubuntu-config-test" and .state == "Running")' && \
	&& multipass list --snapshots --format json | jq -e '.info["ubuntu-config-test"]' && \
	&& multipass restore -d ubuntu-config-test.initial-setup || echo "No VM to restore"

down-vm: ## Stop the VM
	@multipass list | grep -q ubuntu-config-test && (multipass delete -v -p ubuntu-config-test) || echo "VM is already down"

test-docker: ## Test playbook against test container
	@docker-compose exec --user kasm-user ubuntu sh -c 'wget -qO- "http://git/?p=ubuntu-config/.git;a=blob_plain;f=install.sh;hb=refs/heads/main" | bash'

test-vm: ## Test playbook against VM
	docker-compose exec ansible sh -c '/root/.local/bin/ansible-playbook setup.yml \
		--limit ubuntu-config-test \
		-e ANSIBLE_HOST=$(shell multipass info ubuntu-config-test | grep IPv4 | awk '{print $$2}') \
		-e BITWARDEN_EMAIL="$$BITWARDEN_EMAIL" \
		-e BITWARDEN_PASSWORD="$$BITWARDEN_PASSWORD" \
		--diff \
		$(filter-out $@,$(MAKECMDGOALS)) \
	'
define run_linter
	DEFAULT_WORKSPACE="$(CURDIR)"; \
	LINTER_IMAGE="linter:latest"; \
	VOLUME="$$DEFAULT_WORKSPACE:$$DEFAULT_WORKSPACE"; \
	docker build --build-arg UID=$(id -u) --build-arg GID=$(id -g) --tag $$LINTER_IMAGE .; \
	docker run \
		-e DEFAULT_WORKSPACE="$$DEFAULT_WORKSPACE" \
		-e FILTER_REGEX_INCLUDE="$(filter-out $@,$(MAKECMDGOALS))" \
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