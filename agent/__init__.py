"""agent package — terminal-native coding agent runtime."""

from agent.plan import TodoItem, PlanState
from agent.budget import Budget
from agent.hooks import HookBus, destructive_guard
from agent.tools import TOOLS, tool_read_file, tool_run_shell
from agent.loop import run_agent

__all__ = [
    "TodoItem",
    "PlanState",
    "Budget",
    "HookBus",
    "destructive_guard",
    "TOOLS",
    "tool_read_file",
    "tool_run_shell",
    "run_agent",
]
