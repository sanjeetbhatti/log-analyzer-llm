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
3. Create a .env file and add:
    ```
    LLM_BASE_URL=
    LLM_API_KEY=
    LLM_MODEL=
    ```
4. Run the app
    ```
    python src/main.py analyze <log file>
    ```

See help:
```
python src/main.py -h
```
