

def classify_issue(parsed_log: list[str]) -> str:
    if len(parsed_log):
        return "Error"
    return "Unknown issue"