---
name: forget
description: Forget a Claude Code session - close Claude and move every trace of the current session (transcript, prompt history, file history, pastes, plans, scratchpad) to the Bin, or list and forget past sessions. Only when the user types /forget.
disable-model-invocation: true
model: claude-haiku-5-5
argument-hint: "[list [--all] | <session-id>... | --older-than <days>]"
---

# Forget

Script: `~/.claude/skills/forget/forget.py` (run with `python3 -I`). It only touches Claude's own files
(`~/.claude/projects`, `history.jsonl`, `file-history`, `session-env`, `sessions`, `paste-cache`, `plans`,
the `/private/tmp/claude-*` scratchpad) - never the user's project files - and moves them to the Bin with
`/usr/bin/trash`. It refuses to touch sessions that are still running.

Arguments: `$ARGUMENTS`

## No arguments -> forget THIS session

The user typing `/forget` is the confirmation. Do not ask again, do not summarize the conversation.
Run exactly this, as the only tool call, and reply with one short line ("Chiudo Claude e sposto la sessione nel Cestino."):

```
python3 -I ~/.claude/skills/forget/forget.py now
```

Claude closes about 2 seconds later; a detached process then moves the session to the Bin.

## `list` (optionally `--all`, `-n N`)

Run `python3 -I ~/.claude/skills/forget/forget.py list ...` and show the output as a numbered table
(date, short id, first prompt). `[THIS]` is the current session, `[RUNNING]` another open one. Ask which ones to forget.

## Session ids, or `--older-than <days>` -> forget past sessions

1. Run `python3 -I ~/.claude/skills/forget/forget.py delete <ids or --older-than N> --dry-run` and show what would go.
2. Ask for confirmation with one AskUserQuestion (unless the user already named exact ids in this same message).
3. Run the same command without `--dry-run` and report what moved.

Ids can be the full UUID or a prefix of at least 8 characters. Remind the user that items stay in the Bin
until they empty it.
