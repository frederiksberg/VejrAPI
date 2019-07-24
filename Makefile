MAKEFLAGS += --silent
.PHONY: deploy run build clean kill

deploy: | build clean
	docker-compose up -d

run: | build clean
	docker-compose up

build:
	docker-compose build

clean: kill
	docker-compose rm -f

kill:
	docker-compose down
