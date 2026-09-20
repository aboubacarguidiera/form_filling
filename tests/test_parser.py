from types import SimpleNamespace

import anthropic
import httpx2
import pytest

from src.parser import parse_document


class _FakeMessages:
    def __init__(self, result):
        self._result = result

    def create(self, **kwargs):
        if isinstance(self._result, Exception):
            raise self._result
        return self._result


class _FakeClient:
    def __init__(self, result):
        self.messages = _FakeMessages(result)


def _use_fake_client(monkeypatch, result):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-fake-key")
    monkeypatch.setattr(
        "src.parser.anthropic.Anthropic", lambda api_key: _FakeClient(result)
    )


def _fake_message(text):
    return SimpleNamespace(content=[SimpleNamespace(type="text", text=text)])


def _fake_request():
    return httpx2.Request("POST", "https://api.anthropic.com/v1/messages")


def _fake_status_error(status_code, message="error"):
    response = httpx2.Response(status_code, request=_fake_request())
    return anthropic.APIStatusError(message, response=response, body=None)


def test_parse_document_returns_parsed_json(monkeypatch):
    _use_fake_client(monkeypatch, _fake_message('{"Nom": "Dupont"}'))

    result = parse_document("some source text", ["Nom"])

    assert result == {"Nom": "Dupont"}


def test_parse_document_strips_markdown_backticks(monkeypatch):
    _use_fake_client(monkeypatch, _fake_message('```json\n{"Nom": "Dupont"}\n```'))

    result = parse_document("some source text", ["Nom"])

    assert result == {"Nom": "Dupont"}


def test_parse_document_returns_raw_output_on_invalid_json(monkeypatch):
    _use_fake_client(monkeypatch, _fake_message("not valid json"))

    result = parse_document("some source text", ["Nom"])

    assert result == {"raw_output": "not valid json"}


def test_parse_document_missing_api_key_returns_empty_dict(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(
        "src.parser.anthropic.Anthropic",
        lambda api_key: pytest.fail("client should not be constructed without a key"),
    )

    result = parse_document("some source text", ["Nom"])

    assert result == {}


def test_parse_document_handles_authentication_error(monkeypatch):
    response = httpx2.Response(401, request=_fake_request())
    error = anthropic.AuthenticationError("invalid x-api-key", response=response, body=None)
    _use_fake_client(monkeypatch, error)

    result = parse_document("some source text", ["Nom"])

    assert result == {}


def test_parse_document_handles_rate_limit_error(monkeypatch):
    response = httpx2.Response(429, request=_fake_request())
    error = anthropic.RateLimitError("rate limited", response=response, body=None)
    _use_fake_client(monkeypatch, error)

    result = parse_document("some source text", ["Nom"])

    assert result == {}


def test_parse_document_handles_timeout_error(monkeypatch):
    error = anthropic.APITimeoutError(request=_fake_request())
    _use_fake_client(monkeypatch, error)

    result = parse_document("some source text", ["Nom"])

    assert result == {}


def test_parse_document_handles_generic_api_status_error(monkeypatch):
    error = _fake_status_error(500, "internal error")
    _use_fake_client(monkeypatch, error)

    result = parse_document("some source text", ["Nom"])

    assert result == {}


def test_parse_document_handles_connection_error(monkeypatch):
    error = anthropic.APIConnectionError(request=_fake_request())
    _use_fake_client(monkeypatch, error)

    result = parse_document("some source text", ["Nom"])

    assert result == {}
