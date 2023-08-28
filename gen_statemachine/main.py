"""
gen_statemachine entrypoint
"""

import logging
from sys import stdout
from gen_statemachine.diag import LOG_FORMAT
from gen_statemachine.program import Program


def main():
    # The root logger is configured for full verbosity here so
    # that any attached logging handlers can configure the
    # desired verbosity themselves
    logging.getLogger().setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler(stream=stdout)
    stream_handler.setLevel(level=logging.INFO)
    stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logging.getLogger().addHandler(stream_handler)

    program = Program(
        enable_stdout_debug=lambda: stream_handler.setLevel(logging.DEBUG)
    )
    program.run()


if __name__ == "__main__":
    main()
