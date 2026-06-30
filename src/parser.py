import re


ERROR_REGEXP = re.compile(r"\b\w*error\w*\b", re.IGNORECASE)


def parse_log(log_text: str) -> list[str]:
    parsed_data: list[str] = []

    for line in log_text.splitlines():
        ln = line.strip()
        if not ln:
            continue
        
        if ERROR_REGEXP.search(ln):
            parsed_data.append(ln)

    return parsed_data
