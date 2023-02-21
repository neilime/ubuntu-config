.PHONY: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build: ## Build Ubuntu image
	@echo "Building image..."
	@DOCKER_BUILDKIT=1 docker build -t "ubuntu-config" --build-arg "VERSION=latest" .

run: ## Run Ubuntu container
	@docker run \
		-itd \
		--name ubuntu-config \
		--privileged \
		--tmpfs /tmp --tmpfs /run \
		-e DISPLAY=${DISPLAY} \
		-v /tmp/.X11-unix:/tmp/.X11-unix \
		-v /sys/fs/cgroup:/sys/fs/cgroup:ro \
		-v ${PWD}:/home/docker/src \
		-v /var/run/docker.sock:/var/run/docker.sock \
		ubuntu-config

shell:
	@$(call exec, bash $(filter-out $@,$(MAKECMDGOALS))) 

test:
	@$(call exec, bash "/test.sh")

test-ci:
	@docker exec ubuntu-config bash "/test.sh"

clean:
	@docker rm -f ubuntu-config

lint: ## Execute linting (https://github.com/github/super-linter)
	LINT_PATH="$(or $(shell readlink -f $(filter-out $@,$(MAKECMDGOALS))),$(CURDIR))"; \
	VOLUME="$$LINT_PATH:/tmp/lint/$(filter-out $@,$(MAKECMDGOALS))"; \
	docker run \
		-e RUN_LOCAL=true -e USE_FIND_ALGORITHM=true -e LOG_LEVEL=WARN -e LOG_FILE="../logs" \
		-v $$VOLUME \
		--rm \
		github/super-linter:slim-v4


## Run ubuntu
define exec
	docker exec -it -u $(shell id -u):$(shell id -g) ubuntu-config $(1)
endef

#############################
# Argument fix workaround
#############################
%:
	@: