from src.classifier import classify_issue
from src.models import ParsedLog


def test_classify_error():
    parsed = ParsedLog(
        errors=["Something failed"],
        warnings=[],
    )
    assert classify_issue(parsed) == "Error"


def test_classify_warning():
    parsed = ParsedLog(
        errors=[],
        warnings=["Something may be wrong"],
    )
    assert classify_issue(parsed) == "Warning"


def test_classify_unknown_when_no_issues():
    parsed = ParsedLog(
        errors=[],
        warnings=[],
    )

    assert classify_issue(parsed) == "Unknown issue"
