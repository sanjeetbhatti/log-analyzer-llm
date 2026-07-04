# Log Analysis assistant

Python cli app that uses llm to analyze logs and write reports.


# Steps to run:
1. Create virtual env and activate it:
    ```
    python3 -m venv .venv
    source .venv/bin/activate
    ```
2. Install requirements
    ```
    pip install -r requirements.txt
    ```
3. Create a .env file and add the following. See *Environment Variables* section for details.
    ```
    LLM_BASE_URL=
    LLM_API_KEY=
    LLM_MODEL=
    LLM_TIMEOUT=
    ```
4. Run the app. See *Usage Examples* section.
    ```
    python src/main.py analyze <log file>
    ```

See help:
```
python src/main.py -h
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| LLM_BASE_URL | Yes | Base URL for LLM API (e.g., http://localhost:8080/v1) |
| LLM_API_KEY | Yes | API key for LLM service |
| LLM_MODEL | Yes | Model identifier (e.g., gpt-4, qwen-3.5) |
| LLM_REQUEST_TIMEOUT | No | Request timeout in seconds (default: 30) |

## Usage Examples

```bash
# Basic analysis with LLM
python src/main.py analyze /path/to/log.txt

# Skip LLM summary
python src/main.py analyze log.txt --no-llm

# JSON output only
python src/main.py analyze log.txt --format json

# Custom output directory
python src/main.py analyze log.txt --output_dir ./output

# RUn tests
python -m pytest
