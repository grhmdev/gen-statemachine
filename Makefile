run:
	poetry run python gen_statemachine/main.py

test:
	poetry run python -m unittest discover

format:
	poetry run python -m black gen_statemachine/*
	poetry run python -m black tests/*

lint:
	poetry run python -m mypy gen_statemachine/

diagrams:
	plantuml examples/*