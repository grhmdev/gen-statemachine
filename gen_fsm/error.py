from dataclasses import dataclass


@dataclass
class ProgramError(RuntimeError):
    error_message: str

    def __str__(self):
        return f"""
=======================================
ʘ︵ʘ oh no!!!
{self.error_message}
=======================================
"""

    def __repr__(self) -> str:
        return self.__str__()
