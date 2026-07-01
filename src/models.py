from dataclasses import dataclass


@dataclass
class ParsedLog:
    errors: list[str]

    @property
    def num_errors(self) -> int:
        return len(self.errors)
