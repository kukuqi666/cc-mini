from unittest.mock import patch
from mini_claude.permissions import PermissionChecker
from mini_claude.tools.file_read import FileReadTool
from mini_claude.tools.bash import BashTool
from mini_claude.tools.file_edit import FileEditTool


def test_read_only_tool_always_allowed():
    checker = PermissionChecker()
    result = checker.check(FileReadTool(), {"file_path": "/tmp/test.txt"})
    assert result == "allow"


def test_auto_approve_allows_everything():
    checker = PermissionChecker(auto_approve=True)
    assert checker.check(BashTool(), {"command": "rm -rf /"}) == "allow"
    assert checker.check(FileEditTool(), {"file_path": "/etc/passwd", "old_string": "x", "new_string": "y"}) == "allow"


def test_bash_prompts_user_and_allows_on_y(monkeypatch):
    checker = PermissionChecker()
    monkeypatch.setattr("builtins.input", lambda _: "y")
    result = checker.check(BashTool(), {"command": "echo hello"})
    assert result == "allow"


def test_bash_prompts_user_and_denies_on_n(monkeypatch):
    checker = PermissionChecker()
    monkeypatch.setattr("builtins.input", lambda _: "n")
    result = checker.check(BashTool(), {"command": "rm something"})
    assert result == "deny"


def test_always_caches_approval(monkeypatch):
    checker = PermissionChecker()
    monkeypatch.setattr("builtins.input", lambda _: "a")
    checker.check(BashTool(), {"command": "echo first"})
    # Second call should NOT prompt — already cached
    with patch("builtins.input", side_effect=AssertionError("should not prompt")):
        result = checker.check(BashTool(), {"command": "echo second"})
    assert result == "allow"
