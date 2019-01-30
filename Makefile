MAKEFLAGS += --silent

deploy: build
	docker-compose -f ./server.yml up -d

run: build
	docker-compose -f ./server.yml up

build: clean
	docker build -t frbsc/vejr:server -f ./server.Dockerfile .

clean:
	docker-compose -f ./server.yml rm -f
