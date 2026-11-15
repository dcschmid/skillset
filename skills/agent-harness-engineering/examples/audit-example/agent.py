"""Deliberately imperfect example agent loop for audit_harness.py.

Bugs are the point: silent exception swallow, secret in prompt, retry without
stop condition. The turn bound exists so the loop itself is finite — the audit
should still flag the recovery and security issues, and never rewrite this
file automatically (code fixes stay proposals)."""
import os

API_KEY = os.environ.get("API_KEY", "")

TOOLS = [{"name": "read", "description": "read a file",
          "parameters": {"type": "object", "properties": {"path": {"type": "string"}}}},
         {"name": "read", "description": "read a file",
          "parameters": {"type": "object", "properties": {"path": {"type": "string"}}}}]


def call_tool(tool, args):
    return {"status": "success", "summary": "ok", "result": open(args["path"]).read()}


def run(task):
    turn = 0
    while turn < 10:
        turn += 1
        prompt = f"key={API_KEY} task={task}"
        try:
            tool = TOOLS[0]
            result = call_tool(tool, {"path": "notes.md"})
            if result["status"] == "success":
                return result
        except Exception:
            pass
    return {"status": "error", "summary": "turn budget hit"}
