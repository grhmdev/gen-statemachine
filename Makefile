install:
	poetry install

test:
	poetry run python -m unittest discover tests/

format:
	poetry run python -m black gen_fsm/*
	poetry run python -m black tests/*

lint:
	poetry run python -m mypy gen_fsm/ --ignore-missing-imports

diagrams:
	plantuml examples/**/*.puml
	plantuml tests/**/*.test
	plantuml gen_fsm/**/*.puml

clean:
	rm -R output/

RUN_GEN_FSM = poetry run python gen_fsm/main.py
RUN_OUTPUT = poetry run python output/main.py

run-output:
	${RUN_OUTPUT}

example-washing-machine:
	${RUN_GEN_FSM} examples/washing_machine.puml ./output
	${RUN_OUTPUT}

example-hello-world:
	${RUN_GEN_FSM} examples/hello_world.puml ./output
	${RUN_OUTPUT}