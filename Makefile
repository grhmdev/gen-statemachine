run:
	poetry run python gen_fsm/main.py

test:
	poetry run python -m unittest discover

format:
	poetry run python -m black gen_fsm/*
	poetry run python -m black tests/*

lint:
	poetry run python -m mypy gen_fsm/ --ignore-missing-imports

diagrams:
	plantuml examples/*.puml
	plantuml tests/**/*.puml