.PHONY: help

MAKEFLAGS += --silent
.DEFAULT_GOAL := help

help: ## Show help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[$$()% a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

lint: ## Execute linting
	DEFAULT_WORKSPACE="$(CURDIR)"; \
	LINTER_IMAGE="linter:latest"; \
	VOLUME="$$DEFAULT_WORKSPACE:$$DEFAULT_WORKSPACE"; \
	docker build --tag $$LINTER_IMAGE .; \
	docker run \
		-e DEFAULT_WORKSPACE="$$DEFAULT_WORKSPACE" \
		-e FILTER_REGEX_INCLUDE="$(filter-out $@,$(MAKECMDGOALS))" \
		-v $$VOLUME \
		--rm \
		$$LINTER_IMAGE

generate-ssh-key: ## Generate ssh key if not exists
	@test -f .ssh/ansible || ssh-keygen -t rsa -b 4096 -C "ansible@localhost" -f .ssh/ansible -q -N ""

setup: ## Setup the project stack
	@${MAKE} generate-ssh-key
	@docker-compose up --remove-orphans --build -d
	@${MAKE} authorize-ssh-key

authorize-ssh-key: ## Authorize ssh key
	@docker-compose exec test sh -c "cat /home/test/.ssh/ansible.pub >> /home/test/.ssh/authorized_keys"

down: ## Stop the project stack
	@docker-compose down --rmi all --remove-orphans

ansible: ## Run ansible
	@docker-compose exec ansible ansible $(filter-out $@,$(MAKECMDGOALS))

ansible-playbook: ## Run ansible-playbook
	@docker-compose exec ansible ansible-playbook $(filter-out $@,$(MAKECMDGOALS))

ansible-galaxy: ## Run ansible-galaxy
	@docker-compose exec ansible ansible-galaxy $(filter-out $@,$(MAKECMDGOALS))

test: ## Test playbook against test container
	@docker-compose exec ansible ansible-playbook setup.yml --limit test $(filter-out $@,$(MAKECMDGOALS))

#############################
# Argument fix workaround
#############################
%:
	@:
