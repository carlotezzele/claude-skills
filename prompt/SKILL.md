---
name: prompt
description: Turn a rough idea into a professional prompt for Claude Opus 5.5. Interviews the user interactively, writes PROMPT.md in a new project folder, asks for confirmation, then starts an Opus session in that folder. Only when the user types /prompt.
disable-model-invocation: true
model: claude-sonnet-5-5
effort: high
argument-hint: "<rough idea of what you want built>"
---

# Prompt

You are running on Sonnet 5.5 (high effort). Your job: turn the user's rough idea into a
professional prompt, then hand it to a fresh **Claude Opus 5.5** session that does the real work.
You do NOT do the work yourself.

Idea: `$ARGUMENTS` (if empty, ask the user what they want to build, in one plain question).

## 1. Interview (interactive)

Use `AskUserQuestion` - never a wall of questions in text.

- Ask in rounds of 1-4 questions, each with 2-4 concrete options (your recommendation first,
  marked "(Recommended)"). The user can always pick "Other".
- Only ask what changes the prompt: goal and audience, scope of the first version, must-haves vs.
  nice-to-haves, tech stack / platform, constraints (budget, deadline, offline, privacy, language),
  look & feel, how "done" is verified, what Opus must NOT do.
- Skip anything the idea already answers or that has an obvious default - pick it and state it.
- Usually 2-3 rounds. Stop when you could write the prompt without guessing.
- Last round always includes:
  - **Project name** - suggest a short kebab-case name (e.g. `habit-tracker`).
  - **Where** - folder under `~/Code/`: `personal`, `clients`, `velthris`, `experiments`
    (default), `tools`.

Reply to the user in the language they wrote in.

## 2. Write the prompt

Write it in **English** (Opus works best with it) unless the user asks otherwise. Note in the
prompt which language the user wants the app/UI and replies in. Structure:

```markdown
# <Project title>

## Role & goal
One paragraph: what to build, for whom, why. The outcome, not the steps.

## Context
Everything learned in the interview that Opus can't infer.

## Requirements
### Must have (v1)
### Nice to have (only after v1 works)
### Out of scope

## Technical constraints
Stack, platform, dependencies, data, hosting, security/privacy rules.

## Way of working
- Start with a short plan in PLAN.md and wait for my approval before writing code.
- Work in small milestones; after each, run it / test it and tell me what changed.
- Ask me when a decision is genuinely mine; otherwise pick sensible defaults and note them.
- Keep a README with how to run it.

## Definition of done
Concrete, checkable criteria (commands that pass, screens that work, etc.).
```

Be specific and concrete, no filler, no ALL-CAPS shouting. Explain *why* behind constraints.

## 3. Create the project folder

```bash
dir=~/Code/<where>/<project-name>
```

If `$dir` already exists and is not empty, ask the user (AskUserQuestion): use it anyway, or pick
another name. Otherwise `mkdir -p "$dir"`, write the prompt to `$dir/PROMPT.md`, and run
`git init -q` there.

## 4. Confirm

Show the full prompt in chat, then ask with `AskUserQuestion`:
"Start Opus 5.5 in `<dir>` with this prompt?" - options: **Start Opus** (Recommended),
**Edit something** (ask what, apply, show again, ask again), **Cancel** (leave the folder and
PROMPT.md, tell the user how to start later).

## 5. Start Opus

Only after "Start Opus":

- **Claude desktop app** (the `mcp__ccd_session__start_session` tool exists; load it with
  ToolSearch if deferred): start a new session with `cwd` = `$dir`, model Opus 5.5
  (`claude-opus-5-5`), title = project name, and the contents of PROMPT.md as its prompt.
  Use initiation "user_asked" (the user just confirmed). Then open it side by side if
  `mcp__ccd_window__open_session_in` is available, so the user watches Opus work.
- **Terminal / anywhere else**: run `~/.claude/skills/prompt/launch.sh "$dir"` - it opens a new
  Terminal window, `cd`s into the folder and runs
  `claude --model claude-opus-5-5 --name <project> "$(cat PROMPT.md)"`.

Finish with one line: where the project is and that Opus is now working on it.
To start again later: `cd <dir> && claude --model claude-opus-5-5 "$(cat PROMPT.md)"`.
