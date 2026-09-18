from __future__ import annotations

import time
from dataclasses import asdict
from typing import Any

from agent.plan import PlanState, TodoItem
from agent.budget import Budget
from agent.hooks import HookBus, destructive_guard
from agent.tools import TOOLS


# ---------------------------------------------------------------------------
# Stub model  --  deterministic 3-turn script (replace with real LLM call)
# ---------------------------------------------------------------------------

SCRIPT = [
    {
        "plan": [("locate target file", "in_progress"),
                 ("read and diagnose", "pending"),
                 ("apply fix and verify", "pending")],
        "tool": ("run_shell", {"cmd": "ls"}),
        "tokens": 1200,
        "cost": 0.02,
    },
    {
        "plan": [("locate target file", "done"),
                 ("read and diagnose", "in_progress"),
                 ("apply fix and verify", "pending")],
        "tool": ("read_file", {"path": "README.md"}),
        "tokens": 900,
        "cost": 0.02,
    },
    {
        "plan": [("locate target file", "done"),
                 ("read and diagnose", "done"),
                 ("apply fix and verify", "done")],
        "tool": None,
        "tokens": 600,
        "cost": 0.01,
    },
]


def model_step(plan: PlanState, turn: int) -> dict[str, Any]:
    """Stubbed model: returns a plan rewrite and an optional tool call."""
    if turn >= len(SCRIPT):
        return {"plan": plan.items, "tool": None, "tokens": 200, "cost": 0.005}
    s = SCRIPT[turn]
    items = [
        TodoItem(i + 1, desc, status)
        for i, (desc, status) in enumerate(s["plan"])
    ]
    return {"plan": items, "tool": s["tool"], "tokens": s["tokens"], "cost": s["cost"]}


# ---------------------------------------------------------------------------
# Main loop  --  plan / act / observe / recover with full hook integration
# ---------------------------------------------------------------------------

def run_agent(task: str, sandbox: str) -> dict[str, Any]:
    plan = PlanState(goal=task, items=[])
    budget = Budget()
    hooks = HookBus()
    trace: list[dict[str, Any]] = []

    hooks.on("PreToolUse", destructive_guard)
    hooks.on("PostToolUse", lambda p: (trace.append({"event": "tool", **p}), p)[1])
    hooks.on("SessionStart", lambda p: (trace.append({"event": "start", **p}), p)[1])
    hooks.on("SessionEnd", lambda p: (trace.append({"event": "end", **p}), p)[1])

    hooks.fire("SessionStart", {"task": task, "sandbox": sandbox, "started_at": time.time()})

    turn = 0
    while True:
        stop = budget.exceeded()
        if stop:
            hooks.fire("Stop", {"reason": stop, "turn": turn})
            break

        step = model_step(plan, turn)
        plan.items = step["plan"]
        budget.step(step["tokens"], step["cost"])

        call = step["tool"]
        if call is None:
            hooks.fire("Stop", {"reason": "complete", "turn": turn})
            break

        name, args = call
        pre = hooks.fire("PreToolUse", {"tool": name, "args": args})
        if pre.get("blocked"):
            hooks.fire("PostToolUse", {
                "tool": name, "blocked": True, "reason": pre.get("reason", "")
            })
            turn += 1
            continue

        try:
            result = TOOLS[name](sandbox, **args)
            hooks.fire("PostToolUse", {"tool": name, "ok": True, "bytes": len(result)})
        except Exception as exc:
            hooks.fire("PostToolUse", {"tool": name, "ok": False, "error": str(exc)})

        turn += 1

    hooks.fire("SessionEnd", {
        "turns": budget.turns_used,
        "tokens": budget.tokens_used,
        "dollars": budget.dollars_used,
    })

    return {"plan": plan.summary(), "budget": asdict(budget), "trace": trace}
