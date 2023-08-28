"""
Contains custom error types common to all layers
"""
from dataclasses import dataclass


@dataclass
class ProgramError(RuntimeError):
    """
    Error class providing a consistent format for
    all program errors. May be initialised directly,
    or subtyped.
    """

    error_message: str

    def __str__(self):
        return f"""
=======================================
ʘ︵ʘ oh no!!
{self.error_message}
=======================================
"""

    def __repr__(self) -> str:
        return self.__str__()
