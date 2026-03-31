from typing import Literal
from .tools.base import Tool

PermissionBehavior = Literal["allow", "deny"]


class PermissionChecker:
    """Read-only tools are auto-allowed. Bash/writes prompt the user (y/n/always)."""

    def __init__(self, auto_approve: bool = False):
        self._auto_approve = auto_approve
        self._always_allow: set[str] = set()

    def check(self, tool: Tool, inputs: dict) -> PermissionBehavior:
        if tool.is_read_only():
            return "allow"
        if self._auto_approve:
            return "allow"
        if tool.name in self._always_allow:
            return "allow"
        return self._prompt_user(tool, inputs)

    def _prompt_user(self, tool: Tool, inputs: dict) -> PermissionBehavior:
        from rich.console import Console
        console = Console()
        console.print(f"\n[bold yellow]Permission required:[/bold yellow] [bold]{tool.name}[/bold]")
        for k, v in inputs.items():
            val = str(v)[:200] + ("..." if len(str(v)) > 200 else "")
            console.print(f"  [dim]{k}:[/dim] {val}")

        while True:
            choice = input("\n  Allow? [y]es / [n]o / [a]lways: ").strip().lower()
            if choice in ("y", "yes"):
                return "allow"
            if choice in ("n", "no"):
                return "deny"
            if choice in ("a", "always"):
                self._always_allow.add(tool.name)
                return "allow"
            console.print("  Please enter y, n, or a.")
