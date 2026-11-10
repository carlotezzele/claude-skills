# Claude Code skills

My own skills for Claude Code. Put a folder in `~/.claude/skills/` to install it.

- **forget/**: `/forget` closes Claude and moves every trace of the current session
  (transcript, history, file history, pastes, plans, scratchpad) to the Bin, or lists
  and forgets past sessions. Never touches project files.
- **cleanup/**: `/cleanup` scans the home folder (read-only `scan.sh`), then proposes
  folder moves, duplicate removal, cache clearing and big/forgotten files, and applies
  only what you approve, always via the Bin.

## License

MIT, see [LICENSE](LICENSE).
