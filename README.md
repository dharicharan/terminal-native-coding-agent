# Terminal-Native Coding Agent

An autonomous, terminal-based coding agent runtime engineered in Python. Built with a bounded plan-act-observe loop, deterministic sandboxed tool execution, and lifecycle verification hooks.

## Features
- **Plan-Act-Observe Control Loop**: Implements explicit state rewrites and turn/budget ceilings to eliminate infinite model drift.
- **Sandboxed Tool Dispatcher**: Path-jailed file inspection (`read_file`) and shell execution (`run_shell`) with output truncation (4KB cap).
- **Pre/Post Verification Hooks**: Intercepts destructive commands (`rm -rf`, system calls) via `PreToolUse` hooks before execution.
- **Self-Correcting Evaluation**: Built-in verification suites capturing syntax and test tracebacks for automated error recovery.

## Architecture

```
User Prompt / CLI
        |
        v
+-----------------------------------------------------------+
|               Plan-Act-Observe Loop Engine                |
|  - Stateful Plan Manager (TodoWrite itemized state)       |
|  - Turn & Budget Guardrails (Max Turns, Token/Dollar Cap) |
+-----------------------------+-----------------------------+
                              |
                              v
                +----------------------------+
                |    Lifecycle Hook Bus      |
                |  - PreToolUse (Guards)     |
                |  - PostToolUse (Telemetry) |
                +--------------+-------------+
                               |
                               v
                +----------------------------+
                |  Sandboxed Tool Dispatcher |
                |  - read_file               |
                |  - run_shell               |
                |  - git operations          |
                +----------------------------+
```

## Quickstart

```bash
python main.py
```
