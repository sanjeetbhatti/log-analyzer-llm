import argparse
import json

from dataclasses import asdict
from pathlib import Path
from string import Template

from openai import OpenAIError

from classifier import classify_issue
from llm import generate_summary, health_check
from models import AnalysisResult
from parser import parse_log
from report import write_md_report, write_json_report


PROMPT_DIR = Path("prompts")


def load_prompt_template(name: str) -> str:
    path = PROMPT_DIR / name

    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {path}")

    return path.read_text(encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Log analysis assistant")
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser(name="analyze", help="Analyze a log file")
    analyze.add_argument("log_file", type=Path, help="Path to log file")
    analyze.add_argument("--output_dir", type=Path, default=Path("reports"), help="Report output dirctory")
    analyze.add_argument("--no-llm", action="store_true", help="Skip LLM summary generation")
    analyze.add_argument(
        "--format",
        choices=["markdown", "json", "both"],
        default="both",
        help="Report format to generate",
    )

    return parser.parse_args()

def _analyze(log_file: Path, output_dir: Path, no_llm: bool, format: str) -> int:
    if not log_file.exists() or not log_file.is_file():
        print(f"Error: log file not found: {log_file}")
        return 1

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    if not output_dir.is_dir():
        print(f"Error: output dir could be found: {output_dir}")
        return 1

    print(f"Loading log file: {log_file}")
    log_text = log_file.read_text()

    print("Parsing log...")
    parsed = parse_log(log_text)

    print("Classifying issue...")
    issue = classify_issue(parsed)

    if no_llm:
        summary = "LLM disabled. Review parsed output and classification."
        print(summary)
    else:
        print("Generating summary...")
        template = Template(
            load_prompt_template("debug_summary.txt")
        )
        prompt = template.substitute(
            issue=issue,
            errors="\n".join(parsed.errors),
        )

        try:
            summary = generate_summary(prompt)
        except ValueError as err:
            print(f"Configuration error: {err}")
            return 1
        except OpenAIError as err:
            print(f"LLM error: {err}")
            return 1

    result = AnalysisResult(
        log_file=log_file,
        parsed=parsed,
        issue=issue,
        summary=summary,
        suggested_actions=[],
    )

    print("Writing report...")
    md_path = None
    json_path = None
    if format in ("markdown", "both"):
        md_path = write_md_report(result, output_dir)
    if format in ("json", "both"):
        json_path = write_json_report(result, output_dir)

    print("Analysis complete")
    if md_path is not None:
            print(f"Markdown report: {md_path}")
    if json_path is not None:
        print(f"JSON report: {json_path}")
    return 0

def main() -> int:
    args = _parse_args()

    if not args.no_llm:
        health = health_check()
        if not health["healthy"]:
            print(health["message"])
            return 1

    if args.command == "analyze":
        return _analyze(args.log_file, args.output_dir, args.no_llm, args.format)

    return 0
        

if __name__ == "__main__":
    main()
