"""
gen_statemachine entrypoint
"""

import logging
from sys import stdout
from gen_statemachine.diag import LOG_FORMAT
from gen_statemachine.program import Program


def main():
    """
    Configures initial logging and then initialises and runs the `Program`
    """
    # Logging handlers attached to the root logger may only
    # log at the same or lower verbosity to the root logger.
    # The root logger is set for full verbosity here which
    # allows any attached handlers to choose from the full
    # range of verbosity levels.
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
