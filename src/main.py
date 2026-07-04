import argparse
import sys

from dataclasses import asdict
from pathlib import Path
from string import Template

from openai import OpenAIError

from classifier import classify_issue
from llm import generate_summary, health_check
from models import AnalysisResult
from parser import parse_log
from report import write_md_report, write_json_report


PROMPT_DIR = Path(__file__).parent.parent / "prompts"
MAX_LOG_SIZE = 5 * 1024 * 1024 # ~ 5 MB limit


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
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as err:
        print(f"Error creating output directory: {err}")
        return 1

    if not output_dir.is_dir():
        print(f"Error: output dir could not be found: {output_dir}")
        return 1

    print(f"Loading log file: {log_file}")
    try:
        log_text = log_file.read_text(encoding="utf-8")
    except OSError as err:
        print(f"Error reading log file: {err}")
        return 1
    except UnicodeDecodeError as err:
        print(f"Error decoding log file as UTF-8: {err}")
        return 1

    print("Parsing log...")
    parsed = parse_log(log_text)

    print("Classifying issue...")
    issue = classify_issue(parsed)

    if no_llm:
        summary = "LLM disabled. Review parsed output and classification."
        print(summary)
    else:
        print("Generating summary...")
        try:
            template = Template(load_prompt_template("debug_summary.txt"))
            prompt = template.substitute(
                issue=issue,
                errors="\n".join(parsed.errors),
            )
        except FileNotFoundError as err:
            print(f"Prompt template not found: {err}")
            return 1
        except KeyError as err:
            print(f"Invalid prompt template: missing variable {err}")
            return 1
        
        try:
            summary = generate_summary(prompt)
        except ValueError as err:
            print(f"Configuration error: {err}")
            return 1
        except (OpenAIError, RuntimeError) as err:
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
    try:
        if format in ("markdown", "both"):
            md_path = write_md_report(result, output_dir)
        if format in ("json", "both"):
            json_path = write_json_report(result, output_dir)
    except OSError as err:
        print(f"Error writing report: {err}")
        return 1

    print("Analysis complete")
    if md_path is not None:
        print(f"Markdown report: {md_path}")
    if json_path is not None:
        print(f"JSON report: {json_path}")
    return 0

def _validate_log_file(log_file: Path) -> bool:
    if not log_file.exists() or not log_file.is_file():
        print(f"Error: log file not found: {log_file}")
        return False

    log_size = log_file.stat().st_size

    if log_size > MAX_LOG_SIZE:
        print(
            f"Error: log file is too large ({log_size / (1024 * 1024):.1f} MB). "
            f"Maximum size is {MAX_LOG_SIZE / (1024 * 1024):.0f} MB."
        )
        return False

    return True

def main() -> int:
    args = _parse_args()

    if args.command == "analyze":
        if not _validate_log_file(args.log_file):
            return 1
        
        if not args.no_llm:
            health = health_check()
            
            if not health["healthy"]:
                print(health["message"])
                print(
                    "LLM is required for summary generation. "
                    "Fix the LLM configuration/connection, or "
                    "rerun with --no-llm to skip summary generation."
                )
                return 1
        
        return _analyze(args.log_file, args.output_dir, args.no_llm, args.format)

    return 1


if __name__ == "__main__":
    sys.exit(main())
