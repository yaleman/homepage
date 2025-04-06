CONTAINER := "ghcr.io/yaleman/homepage"
CONTAINER_TAG := "latest"
default: localrun

# RUn the app locally
localrun:
	uv run uvicorn --factory homepage:get_app --port 8000 --host 0.0.0.0 --reload


# build the docker container
build:
	docker buildx build \
		-t "{{CONTAINER}}:{{CONTAINER_TAG}}" \
		--load \
		.

# run the docker container
run:
	docker run --rm -it \
	-v $(PWD)/links.json:/links.json \
	-v $(PWD)/images:/images \
	--name homepage \
	-p 8000:8000 \
	"{{CONTAINER}}:{{CONTAINER_TAG}}"

# publish the docker container
docker_publish:
	docker buildx build --platform linux/arm64,linux/amd64 \
	--push \
	-t "{{CONTAINER}}:{{CONTAINER_TAG}}" \
	.


# build and run the docker container
build_run: build run


# linting checks
lint:
	uv run mypy --strict homepage
	uv run mypy --strict tests
	uv run ruff check homepage tests

# test all the things
test: lint
	uv run pytest

check: test