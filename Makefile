# Makefile for Project Chimera container workflow

.PHONY: build test clean

# Build the chimera-worker image
build:
	docker build -t chimera-worker:latest .

# Run tests inside a disposable container and remove it afterwards
test:
	docker run --rm --name chimera-test chimera-worker:latest

# Clean dangling docker images and __pycache__ folders
clean:
	docker image prune -f || true
	find . -type d -name '__pycache__' -exec rm -rf {} + || true
# This builds your Docker "Ship"
setup:
	docker build -t chimera-worker .

# This runs the tests inside the "Ship"
test:
	docker run --rm chimera-worker

# This checks if you have your folders in the right place
spec-check:
	@dir skills
	@dir tests
	@dir specs
	@echo "All folders found!"