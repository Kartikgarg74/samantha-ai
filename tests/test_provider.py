"""Tests for the LLM provider."""
import pytest
from ai.provider import LLMProvider


def test_extract_json_commands():
    """Test JSON extraction from LLM response text."""
    provider = LLMProvider.__new__(LLMProvider)  # skip __init__
    provider.provider_name = "none"

    # Valid JSON block
    text = 'Here is the command:\n```json\n{"action": "open", "target": "chrome"}\n```\nDone.'
    result = provider._extract_json_commands(text)
    assert result == {"action": "open", "target": "chrome"}

    # No JSON block
    text = "Just a plain text response with no commands."
    result = provider._extract_json_commands(text)
    assert result is None

    # Malformed JSON
    text = '```json\n{broken json}\n```'
    result = provider._extract_json_commands(text)
    assert result is None


def test_query_no_provider():
    """Test graceful fallback when no LLM is available."""
    provider = LLMProvider.__new__(LLMProvider)
    provider.provider_name = "none"
    result = provider.query("hello")
    assert "text" in result
    assert "hello" in result["text"]
