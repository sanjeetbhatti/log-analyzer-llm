from dataclasses import dataclass
from pathlib import Path


@dataclass
class ParsedLog:
    """
    Represents the parsed structural output extracted from a log file.
    """
    errors: list[str]
    warnings: list[str]

    @property
    def num_errors(self) -> int:
        return len(self.errors)

    @property
    def num_warnings(self) -> int:
        return len(self.warnings)

    @property
    def total_issues(self) -> int:
        return len(self.errors) + len(self.warnings)

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
