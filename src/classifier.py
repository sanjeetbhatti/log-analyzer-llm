from models import ParsedLog


def classify_issue(parsed_log: ParsedLog) -> str:
    """
    Classify the primary nature of the issue based on parsed log metrics.
    """
    if parsed_log.num_errors:
        return "Error"
    elif parsed_log.num_warnings:
        return "Warning"
    return "Unknown issue"
