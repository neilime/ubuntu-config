.PHONY: help

help: ## Display help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

lint: ## Execute linting
	$(call run_linter,)

lint-fix: ## Execute linting and fix
	$(call run_linter, \
		-e FIX_JSON_PRETTIER=true \
		-e FIX_JAVASCRIPT_PRETTIER=true \
		-e FIX_JAVASCRIPT_STANDARD=true \
		-e FIX_YAML_PRETTIER=true \
		-e FIX_MARKDOWN=true \
		-e FIX_MARKDOWN_PRETTIER=true \
		-e FIX_NATURAL_LANGUAGE=true \
		-e FIX_SHELL_SHFMT=true \
	)

setup: ## Setup the project stack
	$(MAKE) setup-ssh-keys
	@docker-compose up --remove-orphans --build -d

down: ## Stop the project stack
	@docker-compose down --rmi all --remove-orphans

.PHONY: ansible
ansible: ## Run ansible
	@docker-compose exec ansible /home/ubuntu/.local/bin/ansible $(filter-out $@,$(MAKECMDGOALS))

ansible-playbook: ## Run ansible-playbook
	@docker-compose exec ansible /home/ubuntu/.local/bin/ansible-playbook $(filter-out $@,$(MAKECMDGOALS))

ansible-galaxy: ## Run ansible-galaxy
	@docker-compose exec ansible /home/ubuntu/.local/bin/ansible-galaxy $(filter-out $@,$(MAKECMDGOALS))

setup-ssh-keys: ## Setup ssh keys for VM access
	./vm/setup-ssh-keys.sh

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
	$(MAKE) setup-ssh-keys
	@multipass list --format json | jq -e '.list[] | select(.name == "ubuntu-config-test" and .state == "Running")' && \
	echo "VM is already up" || ( \
		SSH_PUBLIC_KEY=$$(cat vm/id_rsa.pub) && cat vm/user-data.yml | sed "s#{{ ssh_public_key }}#$$SSH_PUBLIC_KEY#g" | \
		multipass launch lts --name ubuntu-config-test --cpus 4 --disk 15G --memory 4G --timeout 3600 --cloud-init - && \
		multipass stop ubuntu-config-test && \
		multipass snapshot ubuntu-config-test --name "initial-setup" && \
		multipass start ubuntu-config-test \
	)

vm-open: ## Open the VM
	@remmina -c rdp:$(shell multipass info ubuntu-config-test | grep IPv4 | awk '{print $$2}')

vm-shell: ## Open a shell in the VM
	@ssh -X -i vm/id_rsa ubuntu@$(shell multipass info ubuntu-config-test | grep IPv4 | awk '{print $$2}')

vm-restore: ## Restore the VM
	@multipass list --format json | jq -e '.list[] | select(.name == "ubuntu-config-test" and .state == "Running")' && \
	&& multipass list --snapshots --format json | jq -e '.info["ubuntu-config-test"]' && \
	&& multipass restore -d ubuntu-config-test.initial-setup || echo "No VM to restore"

vm-down: ## Stop the VM
	@multipass list | grep -q ubuntu-config-test && (multipass delete -v -p ubuntu-config-test) || echo "VM is already down"

vm-install-script:  ## Run install script on VM
	@echo "Running Ansible playbook on VM..."
	docker-compose exec ansible sh -c '/root/.local/bin/ansible-playbook setup.yml \
		--limit ubuntu-config-test \
		-e ANSIBLE_HOST=$(shell multipass info ubuntu-config-test | grep IPv4 | awk '{print $$2}') \
		--diff \
		$(filter-out $@,$(MAKECMDGOALS)) \
	'

vm-test: ## Test install script result on VM
	@echo "Running TestInfra tests on VM..."
	@VM_IP=$(shell multipass info ubuntu-config-test | grep IPv4 | awk '{print $$2}'); \
	docker compose run --rm test python3 tests/run_tests.py --verbose --host="ssh://ubuntu@$$VM_IP" --user="ubuntu"

define run_linter
	DEFAULT_WORKSPACE="$(CURDIR)"; \
	LINTER_IMAGE="linter:latest"; \
	VOLUME="$$DEFAULT_WORKSPACE:$$DEFAULT_WORKSPACE"; \
	docker build --build-arg UID=$(shell id -u) --build-arg GID=$(shell id -g) --tag $$LINTER_IMAGE .; \
	docker run \
		-e DEFAULT_WORKSPACE="$$DEFAULT_WORKSPACE" \
		-e FILTER_REGEX_INCLUDE="$(filter-out $@,$(MAKECMDGOALS))" \
		-e IGNORE_GITIGNORED_FILES=true \
		-e KUBERNETES_KUBECONFORM_OPTIONS="--schema-location default --schema-location 'https://raw.githubusercontent.com/datreeio/CRDs-catalog/main/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json'" \
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