.PHONY: run

run:
	uvicorn main:app --reload

install:
	poetry install

lint:
	poetry run black .

test:
	poetry run pytest