from pathlib import Path

from src.models import AnalysisResult, ParsedLog


def test_parsed_log_counts_errors():
    parsed = ParsedLog(
        errors=["error 1", "error 2"],
        warnings=[],
    )

    assert parsed.num_errors == 2
    assert parsed.num_warnings == 0
    assert parsed.total_issues == 2

def test_parsed_log_counts_warnings():
    parsed = ParsedLog(
        errors=[],
        warnings=["warning 1", "warning 2", "warning 3"],
    )

    assert parsed.num_errors == 0
    assert parsed.num_warnings == 3
    assert parsed.total_issues == 3


def test_analysis_result():
    parsed = ParsedLog(
        errors=["error"],
        warnings=[],
    )

    result = AnalysisResult(
        log_file=Path("traceback.log"),
        parsed=parsed,
        issue="Error",
        summary="Database connection failed.",
        suggested_actions=["Restart database"],
    )

    assert result.log_file == Path("traceback.log")
    assert result.issue == "Error"
    assert result.summary == "Database connection failed."
    assert result.suggested_actions == ["Restart database"]
