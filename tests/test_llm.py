import pytest

import src.llm as llm


def test_connect_to_client_requires_base_url(monkeypatch):
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_MODEL", "test-model")

    llm._connect_to_client.cache_clear()

    with pytest.raises(ValueError, match="LLM_BASE_URL is missing"):
        llm._connect_to_client()


def test_connect_to_client_requires_api_key(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://localhost")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setenv("LLM_MODEL", "test-model")

    llm._connect_to_client.cache_clear()

    with pytest.raises(ValueError, match="LLM_API_KEY is missing"):
        llm._connect_to_client()


def test_connect_to_client_requires_model(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://localhost")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.delenv("LLM_MODEL", raising=False)

    llm._connect_to_client.cache_clear()

    with pytest.raises(ValueError, match="LLM_MODEL is missing"):
        llm._connect_to_client()


def test_connect_to_client(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://localhost")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("LLM_REQUEST_TIMEOUT", "15")

    fake_client = object()

    def fake_openai(*, base_url, api_key, timeout):
        assert base_url == "https://localhost"
        assert api_key == "test-key"
        assert timeout == 15.0
        return fake_client

    monkeypatch.setattr(llm, "OpenAI", fake_openai)

    llm._connect_to_client.cache_clear()

    client, model = llm._connect_to_client()

    assert client is fake_client
    assert model == "test-model"


def test_health_check_configuration_error(monkeypatch):
    def fake_connect():
        raise ValueError("LLM_API_KEY is missing")

    monkeypatch.setattr(llm, "_connect_to_client", fake_connect)

    result = llm.health_check()

    assert result["healthy"] is False
    assert "LLM_API_KEY is missing" in result["message"]


def test_health_check_openai_error(monkeypatch):
    from openai import OpenAIError

    def fake_connect():
        raise OpenAIError("connection failed")

    monkeypatch.setattr(llm, "_connect_to_client", fake_connect)

    result = llm.health_check()

    assert result["healthy"] is False
    assert "connection failed" in result["message"]
