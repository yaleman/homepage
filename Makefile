CONTAINER=ghcr.io/yaleman/homepage
CONTAINER_TAG=latest

.DEFAULT: localrun
.PHONY: localrun
localrun:
	uv run uvicorn --factory homepage:get_app --port 8000 --host 0.0.0.0 --reload

.PHONY: build
build:
	docker build -t $(CONTAINER):$(CONTAINER_TAG) .

.PHONY: run
run:
	docker run --rm -it \
	-v $(PWD)/links.json:/links.json \
	-v $(PWD)/images:/images \
	-p 8000:8000 \
	$(CONTAINER):$(CONTAINER_TAG)

.PHONY: build_run
build_run: build run
