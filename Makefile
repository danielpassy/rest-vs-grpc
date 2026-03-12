.PHONY: build up down test test-go test-py proto-gen

build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

test: test-go test-py

test-go:
	cd apps/go-server && go test ./...

test-py:
	cd apps/fastapi-client && uv sync --extra dev && uv run pytest tests/ -v

# Run only when proto/gibberish/v1/gibberish.proto changes. Generated files are committed.
proto-gen:
	protoc --go_out=./apps/go-server/gen --go_opt=paths=source_relative \
	       --go-grpc_out=./apps/go-server/gen --go-grpc_opt=paths=source_relative \
	       -I ./proto ./proto/gibberish/v1/gibberish.proto
	cd apps/fastapi-client && uv run python -m grpc_tools.protoc \
	       -I ../../proto \
	       --python_out=./app/gen \
	       --grpc_python_out=./app/gen \
	       ../../proto/gibberish/v1/gibberish.proto

run-go:
	cd apps/go-server && go run .

run-py:
	cd apps/fastapi-client && uv run uvicorn app.main:app --reload --port 8000
