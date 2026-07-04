from dataclasses import dataclass
from pathlib import Path


@dataclass
class ParsedLog:
    """
    Represents the parsed structural output extracted from a log file.
    """
    errors: list[str]

    @property
    def num_errors(self) -> int:
        return len(self.errors)

@dataclass
class AnalysisResult:
    """
    Represents the complete aggregation of log analysis findings and report metadata.
    """
    log_file: Path
    parsed: ParsedLog
    issue: str
    summary: str
    suggested_actions: list[str]
