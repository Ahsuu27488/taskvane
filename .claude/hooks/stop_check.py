"""Stop hook: don't let a session end with code changes but stale docs.

If uncommitted or unpushed changes touch code but neither docs/STATUS.md nor
CHANGELOG.md changed, block once and ask Claude to update them. On the follow-up
stop (stop_hook_active) it always allows, so it can never loop.
"""
import json
import os
import subprocess
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CODE_PREFIXES = ("app.py", "taskvane/", "ui/", "installer/", "build.ps1", "tools/", "website/src/", ".github/workflows/")
DOC_FILES = ("docs/STATUS.md", "CHANGELOG.md")


def run(*cmd):
    try:
        return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=15,
                              encoding="utf-8", errors="replace").stdout
    except Exception:
        return ""


try:
    payload = json.load(sys.stdin)
except Exception:
    payload = {}
if payload.get("stop_hook_active"):
    sys.exit(0)

changed = set()
for line in run("git", "status", "--porcelain").splitlines():
    path = line[3:].strip().strip('"')
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    changed.add(path.replace("\\", "/"))
# commits not yet on origin count too (work done this session but not pushed)
changed.update(p.strip().replace("\\", "/") for p in run("git", "diff", "--name-only", "@{u}..HEAD").splitlines() if p.strip())

code = sorted(p for p in changed if p.startswith(CODE_PREFIXES))
docs = [p for p in changed if p in DOC_FILES]

if code and not docs:
    print(json.dumps({
        "decision": "block",
        "reason": (
            "Code changed but the project docs didn't: " + ", ".join(code[:8]) + (" …" if len(code) > 8 else "") +
            ". Before stopping, update docs/STATUS.md (what changed, current state, next steps) and add any "
            "user-visible change to CHANGELOG.md (under '## Unreleased' if there's no version bump). Add new traps "
            "or design choices to CLAUDE.md / docs/DECISIONS.md. If these changes are only experiments you'll "
            "revert, say so and stop."
        ),
    }))
sys.exit(0)
