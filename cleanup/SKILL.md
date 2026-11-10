---
name: cleanup
description: Scan the home folder and tidy it up - suggest a better folder structure, find duplicate files, clear regenerable caches, and find big or forgotten files worth deleting. Use for /cleanup, "free up space", "disk is full", "clean my Mac", "find duplicates", "organize my files".
disable-model-invocation: true
---

# Cleanup

Help the user reclaim disk space and organize their home folder. **Scan first, propose, then act only on what they approve.** Reply in the user's language.

The scanner is read-only: `~/.claude/skills/cleanup/scan.sh <mode> [root]`. Modes:

| Mode | What it shows |
|---|---|
| `overview` | disk free, largest top-level folders, loose files in `~` |
| `loose` | file types in home / Desktop / Downloads / Documents, code projects living outside `~/Code` |
| `dupes` | identical files (same size + SHA-1) over 5MB (`MIN_DUPE_MB=` to change) |
| `caches` | regenerable caches, `~/Library/Caches` breakdown, `node_modules` / build folders with project age |
| `big` | files over 200MB with last-modified and last-opened dates (`MIN_BIG_MB=`) |
| `stale` | big files not opened in 180 days, leftover installers and archives (`STALE_DAYS=`) |

`dupes` and `big` can take a few minutes on a full home folder - run them in the background, and pass a subfolder as `root` when the user asks about one place.

## Workflow

1. **Scan.** Run `overview`, then `loose`, `caches`, `big`, `stale`, `dupes` (independent; run in parallel where possible). Read only file names, sizes and dates - never open personal documents to look at their contents.
2. **Report** in four sections, each with sizes and a total "you can free about X GB":
   - **Better folders** - a proposed structure (e.g. `~/Code/<project>` for every repo, `~/Documents/School`, `~/Documents/Work/<client>`, `~/Media/...`) with a concrete move list: `from -> to`. Base it on what is actually there; keep the user's existing good folders. Desktop and Downloads should end up near empty.
   - **Duplicates** - each group, which copy to keep (the one in the best-organized location, or the oldest original) and which to remove.
   - **Caches** - each cache, its size, and the exact command to clear it (table below).
   - **Big / forgotten files** - each candidate, its size, when it was last opened, and why it looks useless (installer already installed, archive already extracted next to it, old export, video duplicated in Photos...). Say "keep" when unsure.
3. **Ask** with one AskUserQuestion: clear caches / remove duplicates / remove big files / apply folder moves, with a "let me pick" option. Never assume consent from an earlier answer.
4. **Apply** only the approved groups, then rerun `overview` and report the space gained and exactly what changed.

## Safe ways to clean

Personal files (duplicates, big files): **always `trash <path>`** (macOS `/usr/bin/trash`) so they can be restored from the Bin - never `rm`. Tell the user to empty the Bin themselves once happy.

Caches: prefer the tool's own command; they rebuild automatically.

| Cache | Command |
|---|---|
| npm | `npm cache clean --force` |
| pnpm | `pnpm store prune` |
| bun | `bun pm cache rm` |
| Homebrew | `brew cleanup --prune=all` |
| Playwright browsers | `npx playwright uninstall --all` (reinstall with `npx playwright install`) |
| Xcode DerivedData / CoreSimulator caches | `rm -rf` the folder (Xcode rebuilds it) |
| Go modules | `go clean -modcache` |
| pip | `pip cache purge` |
| `~/Library/Caches/<app>` | quit the app first, then `rm -rf` that app's subfolder |
| `node_modules` of projects untouched for months | `rm -rf <project>/node_modules` (restore with `npm install`) |

Folder moves: `mv -n` (never overwrite). Before moving a git repo, check `git status` is clean; after moving a project deployed with Vercel, mention the `.vercel` link still works because it lives inside the folder.

## Never touch

- `~/.ssh`, `~/.gnupg`, keychains, `.env*` files, password or credential stores.
- `~/Library` outside `Caches`, `Logs` and Xcode developer caches (app data, Mail, Messages, Photos live there).
- Photos / Music libraries, iCloud Drive placeholders, anything in `~/.claude` (use `/doctor` for that).
- Git history (`.git`), or any project's source - only its regenerable build output.
- Anything the user did not approve in this session.

If something looks important but unclear, list it as "keep - ask me" rather than proposing deletion.
