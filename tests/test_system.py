"""Tests for system action — input sanitization."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from actions.system import _sanitize_app_name
import pytest


class TestSanitizeAppName:

    def test_valid_name(self):
        assert _sanitize_app_name("Safari") == "Safari"

    def test_valid_name_with_spaces(self):
        assert _sanitize_app_name("Google Chrome") == "Google Chrome"

    def test_valid_name_with_hyphen(self):
        assert _sanitize_app_name("VS-Code") == "VS-Code"

    def test_rejects_semicolons(self):
        with pytest.raises(ValueError):
            _sanitize_app_name("Safari; rm -rf /")

    def test_rejects_backticks(self):
        with pytest.raises(ValueError):
            _sanitize_app_name("`malicious`")

    def test_rejects_pipes(self):
        with pytest.raises(ValueError):
            _sanitize_app_name("app | cat /etc/passwd")

    def test_rejects_too_long(self):
        with pytest.raises(ValueError):
            _sanitize_app_name("A" * 101)

    def test_strips_whitespace(self):
        assert _sanitize_app_name("  Firefox  ") == "Firefox"
