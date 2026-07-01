from models import ParsedLog


def classify_issue(parsed_log: ParsedLog) -> str:
    if parsed_log.num_errors:
        return "Error"
    return "Unknown issue"
