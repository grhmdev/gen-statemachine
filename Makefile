install:
	poetry install

test:
	poetry run python -m unittest discover tests/

format:
	poetry run python -m black gen_statemachine/*
	poetry run python -m black tests/*

lint:
	poetry run python -m mypy gen_statemachine/ --ignore-missing-imports

diagrams:
	plantuml examples/**/*.puml
	plantuml tests/**/*.test
	plantuml gen_statemachine/**/*.puml

clean:
	rm -rf output/

RUN_GEN_STATEMACHINE = poetry run python gen_statemachine/main.py
RUN_OUTPUT = poetry run python output/main.py

run-output:
	${RUN_OUTPUT}

example-washing-machine:
	${RUN_GEN_STATEMACHINE} examples/washing_machine.puml ./output
	${RUN_OUTPUT}

example-hello-world:
	${RUN_GEN_STATEMACHINE} examples/hello_world.puml ./output
	${RUN_OUTPUT}