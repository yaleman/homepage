.DEFAULT: build_run

.PHONY: build
build:
	docker build -t ghcr.io/yaleman/homepage:latest .

.PHONY: run
run:
	docker run --rm -it \
	-v $(PWD)/links.json:/links.json \
	-v $(PWD)/homepage/static:/homepage/static \
	-p 8000:8000 \
	ghcr.io/yaleman/homepage:latest

build_run:
	build
	run
