"""SessionStart hook: give every new/resumed session live project state.

Prints JSON with hookSpecificOutput.additionalContext: git branch and status, unpushed
commits, recent commits, latest CI runs, and a warning if docs are older than the code.
Must never fail the session: every step is best-effort.
"""
import json
import os
import subprocess
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CODE = ["app.py", "taskvane", "ui", "installer", "build.ps1", "tools", "website/src", ".github"]
DOCS = ["docs/STATUS.md", "CHANGELOG.md", "CLAUDE.md"]


def run(*cmd, timeout=15):
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        return r.stdout.strip()
    except Exception:
        return ""


def last_commit_time(paths):
    out = run("git", "log", "-1", "--format=%ct", "--", *paths)
    return int(out) if out.isdigit() else 0


lines = ["## Live project state (from the SessionStart hook)"]

branch = run("git", "rev-parse", "--abbrev-ref", "HEAD")
lines.append(f"- Branch: `{branch or '?'}`")

status = run("git", "status", "--short")
if status:
    lines.append(f"- Uncommitted changes ({len(status.splitlines())} files):\n```\n{status[:1500]}\n```")
else:
    lines.append("- Working tree clean.")

run("git", "fetch", "--quiet", "origin", timeout=20)
ahead = run("git", "rev-list", "--count", "@{u}..HEAD")
behind = run("git", "rev-list", "--count", "HEAD..@{u}")
if ahead and ahead != "0":
    lines.append(f"- **{ahead} commit(s) not pushed** to origin.")
if behind and behind != "0":
    lines.append(f"- **{behind} commit(s) on origin not pulled** — pull before editing.")

log = run("git", "log", "-8", "--format=%h %ad %s", "--date=short")
if log:
    lines.append(f"- Recent commits:\n```\n{log}\n```")

tags = run("git", "tag", "--sort=-creatordate")
if tags:
    lines.append(f"- Latest release tag: `{tags.splitlines()[0]}`")

ci = run("gh", "run", "list", "--limit", "4", "--json", "workflowName,status,conclusion,headBranch,createdAt",
         "--jq", '.[] | "\\(.workflowName): \\(.status) \\(.conclusion // "") (\\(.createdAt[:16]))"', timeout=20)
if ci:
    lines.append(f"- Latest CI runs:\n```\n{ci}\n```")
    if "failure" in ci:
        lines.append("- **A CI run failed** — check `gh run list` / `gh run view --log-failed` before new work.")

code_t, status_t = last_commit_time(CODE), last_commit_time(["docs/STATUS.md"])
if code_t and status_t and code_t > status_t:
    lines.append("- **docs/STATUS.md is older than the latest code commit** — read the recent commits and bring it up to date.")

lines.append("Read docs/STATUS.md (next steps) and the traps in CLAUDE.md before changing code.")

print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "\n".join(lines)}}))
sys.exit(0)
