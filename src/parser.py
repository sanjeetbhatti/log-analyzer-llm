import re

from .models import ParsedLog


LOG_START_REGEXP = re.compile(
    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}"
)
LOG_REGEXP = re.compile(
    r"\b(error|err|critical|fatal|exception|fail|failed|failure|timeout)\b",
    re.IGNORECASE
)
WARNING_REGEXP = re.compile(
    r"\b(warn|warning)\b",
    re.IGNORECASE,
)


def parse_log(log_text: str) -> ParsedLog:
    """
    Parse raw log text, extracting non-empty lines that contain error-related terms.
    """
    lines = log_text.splitlines()
    entries: list[list[str]] = []
    current_entry: list[str] = []

    for line in lines:
        if LOG_START_REGEXP.match(line):
            if current_entry:
                entries.append(current_entry)
                current_entry = []
            current_entry.append(line)
        else:
            if current_entry:
                current_entry.append(line)
            else:
                if line.strip():
                    entries.append([line])

    if current_entry:
        entries.append(current_entry)

    errors: list[str] = []
    warnings: list[str] = []

    for entry_lines in entries:
        entry = "\n".join(entry_lines).strip()
        if not entry:
            continue
        
        if (LOG_REGEXP.search(entry) or 
            re.search(r"\btraceback\b", entry, re.IGNORECASE)):
            errors.append(entry)
        elif WARNING_REGEXP.search(entry):
            warnings.append(entry)

    return ParsedLog(errors=errors, warnings=warnings)
