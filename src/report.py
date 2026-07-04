import json
from dataclasses import asdict
from pathlib import Path

from models import AnalysisResult


def write_report(result: AnalysisResult, output_dir: Path) -> Path:
    report_path = output_dir / f"{result.log_file.stem}_report.json"

    payload = {
        "log_file": str(result.log_file),
        "issue": result.issue,
        "summary": result.summary,
        "suggested_actions": result.suggested_actions,
        "parsed": asdict(result.parsed),
        "num_errors": result.parsed.num_errors,
    }
    
    report_path.write_text(json.dumps(payload, indent=2))
    return report_path
