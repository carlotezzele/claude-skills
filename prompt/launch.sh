#!/bin/zsh
# Usage: launch.sh <project-dir>
# Opens a new Terminal window in <project-dir> running Claude Opus 5.5 on PROMPT.md.
set -euo pipefail
dir="${1:?project dir required}"
[[ -f "$dir/PROMPT.md" ]] || { echo "missing $dir/PROMPT.md" >&2; exit 1; }
name="${dir:t}"
cmd="cd ${(q)dir} && claude --model claude-opus-5-5 --name ${(q)name} \"\$(cat PROMPT.md)\""
osascript - "$cmd" <<'OSA'
on run argv
  tell application "Terminal"
    activate
    do script (item 1 of argv)
  end tell
end run
OSA
echo "Opus started in Terminal: $dir"
