import json
from dataclasses import asdict
from pathlib import Path

from .models import AnalysisResult


def write_json_report(result: AnalysisResult, output_dir: Path) -> Path:
    """
    Generate and write a JSON format analysis report.
    """
    report_path = output_dir / f"{result.log_file.stem}_report.json"

    payload = {
        "log_file": str(result.log_file),
        "issue": result.issue,
        "summary": result.summary,
        "suggested_actions": result.suggested_actions,
        "parsed": asdict(result.parsed),
        "num_errors": result.parsed.num_errors,
        "num_warnings": result.parsed.num_warnings,
    }
    
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return report_path

def write_md_report(result: AnalysisResult, output_dir: Path) -> Path:
    """
    Generate and write a Markdown format analysis report.
    """
    report_path = output_dir / f"{result.log_file.stem}_report.md"

    if result.parsed.errors:
        parsed_errors = "\n\n".join(
            f"```text\n{err.strip()}\n```" 
            for err in result.parsed.errors[:10]
        )
    else:
        parsed_errors = "- No errors found"

    if result.parsed.warnings:
        parsed_warnings = "\n\n".join(
            f"```text\n{warn.strip()}\n```" 
            for warn in result.parsed.warnings[:10]
        )
    else:
        parsed_warnings = "- No warnings found"

    action_text = "\n".join(f"- {item}" for item in result.suggested_actions)
    if not action_text:
        action_text = "- No suggested actions"

    content = (
        "# Analysis Report\n\n"
        "## File\n"
        f"{result.log_file}\n\n"
        "## Statistics\n"
        f"- Errors: {result.parsed.num_errors}\n\n"
        f"- Warnings: {result.parsed.num_warnings}\n\n"
        "## Classification\n"
        f"{result.issue}\n\n"
        "## AI Summary\n"
        f"{result.summary}\n\n"
        "## Parsed Errors\n"
        f"{parsed_errors}\n\n"
        "## Parsed Warnings\n"
        f"{parsed_warnings}\n\n"
        "## Suggested Actions\n"
        f"{action_text}\n"
    )

    report_path.write_text(content, encoding="utf-8")
    return report_path
