import argparse
import logging
import sys

from logging.handlers import RotatingFileHandler
from pathlib import Path
from string import Template

from openai import OpenAIError

from .classifier import classify_issue
from .llm import generate_summary, health_check
from .models import AnalysisResult
from .parser import parse_log
from .report import write_md_report, write_json_report


PROMPT_DIR = Path(__file__).parent.parent / "prompts"
MAX_LOG_SIZE = 5 * 1024 * 1024 # ~ 5 MB limit

logger = logging.getLogger(__name__)

def _setup_logging(output_dir: Path) -> None:
    """
    Configure logging to write to stdout as well as rotating file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    log_file = output_dir / "analysis.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler(
                log_file,
                maxBytes=MAX_LOG_SIZE,
                backupCount=3,
            )
        ],
        force=True
    )

def load_prompt_template(name: str) -> str:
    """
    Load pre-written prompt template file.
    """
    path = PROMPT_DIR / name

    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {path}")

    return path.read_text(encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    """
    Parse all command line arguments.
    """
    parser = argparse.ArgumentParser(description="Log analysis assistant")
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser(
        "analyze",
        help="Analyze a log file and generate reports",
        description="Analyze a log file using LLM to classify issues and generate summaries.",
    )
    analyze.add_argument("log_file", type=Path, help="Path to log file")
    analyze.add_argument(
        "--output_dir", 
        type=Path, 
        default=Path(__file__).parent.parent / "reports",
        help="Report output directory (default: ./reports)",
    )
    analyze.add_argument("--no-llm", action="store_true", help="Skip LLM summary generation")
    analyze.add_argument(
        "--format",
        choices=["markdown", "json", "both"],
        default="both",
        help="Report format to generate",
    )

    return parser.parse_args()

def _analyze(log_file: Path, output_dir: Path, no_llm: bool, format: str) -> int:
    """
    Run analysis pipeline.
    - Load input log file
    - Parse log file to get ParsedLog structured format
    - Classify the issue detected
    - Generate LLM summary (enabled by default)
    - Write to summary files (default: both json and markdown formats)
    """
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as err:
        logger.exception("Error creating output directory: %s", err)
        return 1

    if not output_dir.is_dir():
        logger.error("Error: output dir could not be found: %s", output_dir)
        return 1

    logger.info("[1/5] Loading log file: %s", log_file)
    try:
        log_text = log_file.read_text(encoding="utf-8")
    except OSError as err:
        logger.exception("Error reading log file: %s", err)
        return 1
    except UnicodeDecodeError as err:
        logger.exception("Error decoding log file as UTF-8: %s", err)
        return 1

    logger.info("[2/5] Parsing log...")
    parsed = parse_log(log_text)

    logger.info("[3/5] Classifying issue...")
    issue = classify_issue(parsed)

    if no_llm:
        logger.info("[4/5] Generating summary - skipped")
        summary = "LLM disabled. Review parsed output and classification."
        logger.warning(summary)
    else:
        logger.info("[4/5] Generating summary...")
        try:
            template = Template(load_prompt_template("debug_summary.txt"))
            prompt = template.substitute(
                issue=issue,
                errors="\n".join(parsed.errors),
            )
        except FileNotFoundError as err:
            logger.exception("Prompt template not found: %s", err)
            return 1
        except KeyError as err:
            logger.exception("Invalid prompt template: missing variable %s", err)
            return 1
        
        try:
            summary = generate_summary(prompt)
        except ValueError as err:
            logger.exception("Configuration error: %s", err)
            return 1
        except (OpenAIError, RuntimeError) as err:
            logger.exception("LLM error: %s", err)
            return 1

    result = AnalysisResult(
        log_file=log_file,
        parsed=parsed,
        issue=issue,
        summary=summary,
        suggested_actions=[],
    )

    logger.info("[5/5] Writing report...")
    md_path = None
    json_path = None
    try:
        if format in ("markdown", "both"):
            md_path = write_md_report(result, output_dir)
        if format in ("json", "both"):
            json_path = write_json_report(result, output_dir)
    except OSError as err:
        logger.exception("Error writing report: %s", err)
        return 1

    logger.info("Analysis complete")
    if md_path is not None:
        logger.info("Markdown report: %s", md_path)
    if json_path is not None:
        logger.info("JSON report: %s", json_path)
    return 0

def _validate_log_file(log_file: Path) -> bool:
    """
    Validate that the target input log file exists and is within set size limits.
    """
    if not log_file.exists() or not log_file.is_file():
        logger.error("Error: log file not found: %s", log_file)
        return False

    log_size = log_file.stat().st_size

    if log_size > MAX_LOG_SIZE:
        logger.error(
            "Error: log file is too large (%.1f MB). Maximum size is %.0f MB.",
            log_size / (1024 * 1024),
            MAX_LOG_SIZE / (1024 * 1024)
        )
        return False

    return True

def main() -> int:
    args = _parse_args()

    if args.command == "analyze":
        # make sure analysis log file is properly set
        _setup_logging(args.output_dir)

        if not _validate_log_file(args.log_file):
            return 1
        
        if not args.no_llm:
            health = health_check()
            
            if not health["healthy"]:
                logger.error(health["message"])
                logger.error(
                    "LLM is required for summary generation. "
                    "Fix the LLM configuration/connection, or "
                    "rerun with --no-llm to skip summary generation."
                )
                return 1
        
        return _analyze(args.log_file, args.output_dir, args.no_llm, args.format)

    return 1


if __name__ == "__main__":
    sys.exit(main())
