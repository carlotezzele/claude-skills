# Claude Code skills

My own skills for Claude Code. Put a folder in `~/.claude/skills/` to install it.

- **forget/**: `/forget` closes Claude and moves every trace of the current session
  (transcript, history, file history, pastes, plans, scratchpad) to the Bin, or lists
  and forgets past sessions. Never touches project files.
- **cleanup/**: `/cleanup` scans the home folder (read-only `scan.sh`), then proposes
  folder moves, duplicate removal, cache clearing and big/forgotten files, and applies
  only what you approve, always via the Bin.
- **prompt/**: `/prompt <idea>` runs on Sonnet 5.5 (high effort), interviews you with
  interactive questions, writes a professional `PROMPT.md` for Claude Opus 5.5 in a new
  `~/Code/<area>/<project>` folder, asks for confirmation, then starts an Opus session there
  (desktop app session, or a new Terminal window via `launch.sh`).

## License

MIT, see [LICENSE](LICENSE).
