from __future__ import annotations

from typing import Any, Callable

HookFn = Callable[[dict[str, Any]], dict[str, Any]]


class HookBus:
    EVENTS = (
        "SessionStart",
        "SessionEnd",
        "PreToolUse",
        "PostToolUse",
        "UserPromptSubmit",
        "Notification",
        "Stop",
        "PreCompact",
    )

    def __init__(self) -> None:
        self._hooks: dict[str, list[HookFn]] = {e: [] for e in self.EVENTS}

    def on(self, event: str, fn: HookFn) -> None:
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(fn)

    def fire(self, event: str, payload: dict[str, Any]) -> dict[str, Any]:
        for fn in self._hooks.get(event, []):
            payload = fn(payload) or payload
        return payload


def destructive_guard(payload: dict[str, Any]) -> dict[str, Any]:
    """PreToolUse guard blocking destructive shell commands."""
    cmd = payload.get("args", {}).get("cmd", "")
    if "rm -rf" in cmd or "shutdown" in cmd:
        payload["blocked"] = True
        payload["reason"] = "destructive command blocked by PreToolUse hook"
    return payload
