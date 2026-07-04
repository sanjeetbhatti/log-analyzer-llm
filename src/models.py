from dataclasses import dataclass
from pathlib import Path


@dataclass
class ParsedLog:
    errors: list[str]

    @property
    def num_errors(self) -> int:
        return len(self.errors)

@dataclass
class AnalysisResult:
    log_file: Path
    parsed: ParsedLog
    issue: str
    summary: str
    suggested_actions: list[str]
