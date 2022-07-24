.DEFAULT: localrun
.PHONY: localrun
localrun:
	uvicorn homepage:app --port 8000 --host 0.0.0.0 --reload

.PHONY: build
build:
	docker build -t ghcr.io/yaleman/homepage:latest .

.PHONY: run
run:
	docker run --rm -it \
	-v $(PWD)/links.json:/links.json \
	-v $(PWD)/images:/images \
	-p 8000:8000 \
	ghcr.io/yaleman/homepage:latest

.PHONY: build_run
build_run: build run

.PHONY: test
test:
	poetry install
	poetry run mypy --strict homepage
	poetry run mypy --strict tests
	poetry run pylint homepage tests
	poetry run pytest