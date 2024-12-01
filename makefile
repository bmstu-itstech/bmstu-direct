.DEFAULT_GOAL := start

REQUIREMENTS := "requirements.txt"

.PHONY: install
install:
	poetry install \
		--no-root

.PHONY: run-local
run-local: .env
	poetry run python3 main.py

.PHONY: start
start: .env
	docker compose --env-file=.env up -d

.PHONY: stop
stop:
	docker compose down

.PHONY: export
export:
	poetry export -o $(REQUIREMENTS) \
		--without-hashes

.env:
	cp .env.example .env
