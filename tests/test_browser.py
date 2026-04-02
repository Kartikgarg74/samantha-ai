"""Tests for browser action — URL validation and command parsing."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from actions.browser import _validate_url, browser_action


class TestUrlValidation:

    def test_allows_https(self):
        assert _validate_url("https://github.com") is True

    def test_allows_http(self):
        assert _validate_url("http://example.com") is True

    def test_blocks_javascript(self):
        assert _validate_url("javascript:alert('xss')") is False

    def test_blocks_file(self):
        assert _validate_url("file:///etc/passwd") is False

    def test_blocks_localhost(self):
        assert _validate_url("http://localhost:8080") is False

    def test_blocks_127(self):
        assert _validate_url("http://127.0.0.1") is False

    def test_blocks_private_ip(self):
        assert _validate_url("http://192.168.1.1") is False
        assert _validate_url("http://10.0.0.1") is False

    def test_allows_normal_domain(self):
        assert _validate_url("https://www.google.com") is True


class TestBrowserAction:

    def test_search_command(self):
        response, action_type = browser_action("search for machine learning")
        assert action_type == "browser_search"
        assert "machine learning" in response.lower()

    def test_unknown_command(self):
        response, action_type = browser_action("do something weird")
        assert action_type == "browser_unknown"
