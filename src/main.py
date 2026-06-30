import argparse
import json
from pathlib import Path

from classifier import classify_issue
from parser import parse_log


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Log analysis assistant")
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser(name="analyze", help="Analyze a log file")
    analyze.add_argument("log_file", type=Path, help="Path to log file")
    analyze.add_argument("--output_dir", type=Path, default=Path("reports"), help="Report output dirctory")

    return parser.parse_args()

def _analyze(log_file: Path, output_dir: Path):
    if not log_file.exists() or not log_file.is_file():
        print(f"Error: log file not found: {log_file}")
        return

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    if not output_dir.is_dir():
        print(f"Error: output dir could be found: {output_dir}")
        return

    print(f"Loading log file: {log_file}")
    log_text = log_file.read_text()

    print("Parsing log...")
    parsed = parse_log(log_text)

    print("Classifying issue...")
    issue = classify_issue(parsed)

    # llm step here

    result = {
        'log_path': str(log_file.stem),
        'issue_type': issue,
        'parsed_log': parsed,
    }

    print("Writing report...")
    report_path = output_dir / f"{result['log_path']}_report.json"
    report_path.write_text(json.dumps(result, indent=2))

    print("Analysis complete")

def main():
    args = _parse_args()

    if args.command == "analyze":
        _analyze(args.log_file, args.output_dir)
        

if __name__ == "__main__":
    main()
