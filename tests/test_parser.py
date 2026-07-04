from src.parser import parse_log


def test_parse_log_extracts_errors():
    log = """\
2026-01-01 10:00:00,123 INFO Starting application
2026-01-01 10:00:01,123 ERROR Database connection failed
2026-01-01 10:00:02,123 INFO Continuing
"""

    result = parse_log(log)

    assert result.num_errors == 1
    assert result.num_warnings == 0
    assert "Database connection failed" in result.errors[0]


def test_parse_log_extracts_warnings():
    log = """\
2026-01-01 10:00:00,123 INFO Starting application
2026-01-01 10:00:01,123 WARNING Cache is nearly full
"""

    result = parse_log(log)

    assert result.num_errors == 0
    assert result.num_warnings == 1
    assert "Cache is nearly full" in result.warnings[0]
