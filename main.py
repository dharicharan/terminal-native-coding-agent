"""Terminal-native coding agent — entry point.

Runs the plan-act-observe-recover loop in a sandboxed environment.
The LLM is stubbed with a deterministic script so the loop stays
testable without any API calls.

Usage:
    python main.py
"""

import json
import os

from agent.loop import run_agent


def main() -> None:
    task = "demonstrate the plan-act-observe loop without network calls"
    sandbox = os.path.dirname(os.path.abspath(__file__))
    result = run_agent(task, sandbox)

    print(result["plan"])
    print("---")
    b = result["budget"]
    print(f"turns={b['turns_used']}  tokens={b['tokens_used']}  dollars=${b['dollars_used']:.3f}")
    print("---")
    print(f"trace events: {len(result['trace'])}")
    for ev in result["trace"]:
        print(" ", json.dumps(ev, default=str))


if __name__ == "__main__":
    main()
