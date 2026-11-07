# Variables
COMPONENTS_DIR := components

# Recursively find all yaml files in components directory and subdirectories
YAML_FILES := $(shell find $(COMPONENTS_DIR) -type f \( -name "*.yaml" -o -name "*.yml" \))

# Extract image names (with debug output)
IMAGES := $(shell for file in $(YAML_FILES); do \
		echo "Processing $$file..." >&2; \
		yq eval '.implementation.container.image' $$file 2>/dev/null | grep -v "null" | sed 's/:latest//'; \
	done)

# Debug target to show variables
.PHONY: debug
debug:
	@echo "Found YAML files: $(YAML_FILES)"
	@echo "Extracted images: $(IMAGES)"
	@for file in $(YAML_FILES); do \
		echo "\nContent from $$file:"; \
		yq eval '.implementation.container.image' $$file; \
	done

# Default target
.PHONY: all
all: build push

# Build all images
.PHONY: build
build: 
	@for file in $(YAML_FILES); do \
		IMAGE_NAME=$$(yq eval '.implementation.container.image' $$file | grep -v "null" | sed 's/:latest//'); \
		if [ -n "$$IMAGE_NAME" ]; then \
			echo "Building $$IMAGE_NAME"; \
			docker build -t $$IMAGE_NAME:latest -f Dockerfile .; \
		fi \
	done

# Push all images
.PHONY: push
push:
	@for file in $(YAML_FILES); do \
		IMAGE_NAME=$$(yq eval '.implementation.container.image' $$file | grep -v "null" | sed 's/:latest//'); \
		if [ -n "$$IMAGE_NAME" ]; then \
			echo "Pushing $$IMAGE_NAME"; \
			docker push $$IMAGE_NAME:latest; \
		fi \
	done

# Build individual image
.PHONY: build-%
build-%:
	@echo "Building $*..."
	@IMAGE_NAME=$$(find $(COMPONENTS_DIR) -type f \( -name "*.yaml" -o -name "*.yml" \) -exec yq eval '.implementation.container.image' {} \; | grep "$*" | sed 's/:latest//'); \
	if [ -n "$$IMAGE_NAME" ]; then \
		echo "Building image: $$IMAGE_NAME"; \
		docker build -t $$IMAGE_NAME:latest -f Dockerfile .; \
	else \
		echo "No image found matching $*"; \
		exit 1; \
	fi

# Push individual image
.PHONY: push-%
push-%:
	@echo "Pushing $*..."
	@IMAGE_NAME=$$(find $(COMPONENTS_DIR) -type f \( -name "*.yaml" -o -name "*.yml" \) -exec yq eval '.implementation.container.image' {} \; | grep "$*" | sed 's/:latest//'); \
	if [ -n "$$IMAGE_NAME" ]; then \
		echo "Pushing image: $$IMAGE_NAME"; \
		docker push $$IMAGE_NAME:latest; \
	else \
		echo "No image found matching $*"; \
		exit 1; \
	fi

# Clean up images
.PHONY: clean
clean:
	@echo "Cleaning up images..."
	@for file in $(YAML_FILES); do \
		IMAGE_NAME=$$(yq eval '.implementation.container.image' $$file | sed 's/:latest//'); \
		if [ -n "$$IMAGE_NAME" ] && [ "$$IMAGE_NAME" != "null" ]; then \
			echo "Removing $$IMAGE_NAME:latest"; \
			docker rmi $$IMAGE_NAME:latest || true; \
		fi \
	done

# List all available images
.PHONY: list
list:
	@echo "Available images to build:"
	@for file in $(YAML_FILES); do \
		echo "From $$file:"; \
		IMAGE=$$(yq eval '.implementation.container.image' $$file); \
		if [ "$$IMAGE" != "null" ]; then \
			echo "  $$IMAGE"; \
		fi \
	done 