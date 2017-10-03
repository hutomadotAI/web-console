# System
SHELL   		:= /bin/bash

# Constants
CONTAINER 		:= eu.gcr.io/playground-project-01/django

# Variable
tag				?= latest
environement	?= production


.PHONY: help


# Targets
clean-containers:	#. Clean all the previous containers
	@echo -e "$(CYAN)$(BOLD)‣ clean-containers $(CONTAINER)$(RESET)"
	@exec 1> >(sed 's/^/  /'); \
		docker image prune --force --all --filter label=container=$(CONTAINER)


build-container: clean-containers	#. Build a new container
	@echo -e "$(CYAN)$(BOLD)‣ build-container $(tag)$(RESET)"
	@exec 1> >(sed 's/^/  /'); \
		docker build \
			--build-arg ENVIRONMENT=$(environement) \
			--build-arg CONTAINER=$(CONTAINER) \
			-t $(CONTAINER):$(tag) .


push-container: build-container	#. Push the container to gCloud
	@echo -e "$(CYAN)$(BOLD)‣ push-container$(RESET)"
	@exec 1> >(sed 's/^/  /'); \
		gcloud docker -- push $(CONTAINER)


apply-deployment: push-container	#. Apply a spcific container to be deployed
	@echo -e "$(CYAN)$(BOLD)‣ apply-deployment$(RESET)"
	@exec 1> >(sed 's/^/  /'); \
		export DJANGO_TAG=$(tag); \
		export CONTAINER=$(CONTAINER); \
		envsubst < kubernetes/deployments/django.yml | kubectl apply -f -;
	@echo -e "$(CYAN)$(BOLD)‣ deploying… (cmd+c to close)$(RESET)"
	@exec 1> >(sed 's/^/  /'); \
		kubectl get pods --watch


build: apply-deployment

# Sugger
help:	#. This help message
	@echo -e "Usage: make [target] [options]"
	@echo -e "\nTargets (Commands):"
	@exec 1> >(sed 's/^/  /'); \
		echo -e "$$(grep -hE '^\S+:.*#' $(MAKEFILE_LIST) | sed -e 's/:.*#\.\s*/:	/' -e 's/^\(.\+\):\(.*\)/\$(CYAN)\1\$(RESET):\2/')";
	@echo -e "\nOptions (Arguments):"
	@exec 1> >(sed 's/^/  /'); \
		echo -e 'tag:		tag=latest'; \
		echo -e 'environement:	environement=production'; \

BOLD	:= \033[1m

BLUE 	:= \033[34m
CYAN 	:= \033[36m
GREEN 	:= \033[32m
RED 	:= \033[31m
YELLOW 	:= \033[33m

RESET 	:= \033[0m
