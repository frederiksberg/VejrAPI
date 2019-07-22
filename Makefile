MAKEFLAGS += --silent
.PHONY: deploy run build clean kill

deploy: build
	docker-compose up -d

run: build
	docker-compose up

build: clean
	docker-compose build

clean: kill
	docker-compose rm -f

kill:
	docker-compose down
