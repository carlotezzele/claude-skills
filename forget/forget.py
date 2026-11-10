#!/usr/bin/env python3
"""forget: move every trace of a Claude Code session to the macOS Bin.

  forget.py now                      forget THIS session: closes Claude, then cleans up
  forget.py list [--all] [-n N]      list sessions (this folder, or every folder)
  forget.py delete ID... [--dry-run] forget past sessions (full id or >=8-char prefix)
  forget.py delete --older-than D    forget every session not touched in D days

Only Claude's own files are touched, never your project files.
Everything goes to the Bin (/usr/bin/trash): empty it to make it permanent.
"""
import glob, json, os, re, signal, subprocess, sys, time

HOME = os.path.expanduser("~")
C = os.path.join(HOME, ".claude")
HIST = os.path.join(C, "history.jsonl")
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def project_dir(cwd):
    return os.path.join(C, "projects", re.sub(r"[^A-Za-z0-9]", "-", cwd))


def all_transcripts():
    out = {}
    for p in glob.glob(os.path.join(C, "projects", "*", "*.jsonl")):
        sid = os.path.basename(p)[:-6]
        if UUID.match(sid):
            out[sid] = p
    return out


def alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def running_sessions():
    """sessionId -> pid for Claude processes still alive."""
    out = {}
    for f in glob.glob(os.path.join(C, "sessions", "*.json")):
        try:
            d = json.load(open(f))
            if alive(int(d["pid"])):
                out[d["sessionId"]] = int(d["pid"])
        except Exception:
            pass
    return out


def read_history():
    try:
        return open(HIST, encoding="utf-8").read().splitlines(keepends=True)
    except FileNotFoundError:
        return []


def first_prompts():
    first = {}
    for line in read_history():
        try:
            d = json.loads(line)
        except Exception:
            continue
        sid = d.get("sessionId")
        if sid and sid not in first:
            first[sid] = d.get("display", "")
    return first


def traces(sid):
    """Every file/folder that belongs only to this session."""
    paths = []
    paths += glob.glob(os.path.join(C, "projects", "*", sid + ".jsonl"))
    paths += [p for p in glob.glob(os.path.join(C, "projects", "*", sid)) if os.path.isdir(p)]
    for sub in ("file-history", "session-env", "todos", "debug"):
        paths += glob.glob(os.path.join(C, sub, sid + "*"))
    for f in glob.glob(os.path.join(C, "sessions", "*.json")):
        try:
            if json.load(open(f)).get("sessionId") == sid:
                paths.append(f)
        except Exception:
            pass
    paths += glob.glob(f"/private/tmp/claude-{os.getuid()}/*/{sid}")
    # plans written in this session, unless another transcript also mentions them
    plans = set()
    for t in [p for p in paths if p.endswith(".jsonl")]:
        try:
            plans |= set(re.findall(r"\.claude/plans/([\w.-]+\.md)", open(t, errors="ignore").read()))
        except Exception:
            pass
    for name in plans:
        plan = os.path.join(C, "plans", name)
        if not os.path.exists(plan):
            continue
        others = subprocess.run(
            ["grep", "-rlF", "--include=*.jsonl", f".claude/plans/{name}", os.path.join(C, "projects")],
            capture_output=True, text=True).stdout.split()
        if all(os.path.basename(o)[:-6] == sid for o in others):
            paths.append(plan)
    return sorted(set(paths))


def scrub_history(sids, dry):
    """Remove the sessions' prompts from history.jsonl and their unused paste-cache files."""
    lines = read_history()
    keep, hashes, removed = [], set(), 0
    for line in lines:
        try:
            d = json.loads(line)
        except Exception:
            keep.append(line)
            continue
        if d.get("sessionId") in sids:
            removed += 1
            for p in (d.get("pastedContents") or {}).values():
                if isinstance(p, dict) and p.get("contentHash"):
                    hashes.add(p["contentHash"])
        else:
            keep.append(line)
    still = "".join(keep)
    pastes = [p for h in hashes if h not in still
              for p in glob.glob(os.path.join(C, "paste-cache", h + "*"))]
    if removed and not dry:
        tmp = HIST + ".forget-tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(still)
        os.chmod(tmp, os.stat(HIST).st_mode & 0o777)
        os.replace(tmp, HIST)
    return removed, pastes


def trash(paths):
    paths = [p for p in paths if os.path.lexists(p)]
    if paths:
        subprocess.run(["/usr/bin/trash", *paths], check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def forget(sids, dry=False, quiet=False):
    paths = []
    for sid in sids:
        paths += traces(sid)
    removed, pastes = scrub_history(set(sids), dry)
    paths += pastes
    if not quiet:
        verb = "Would move" if dry else "Moved"
        print(f"{verb} to the Bin ({len(paths)} items):")
        for p in paths:
            print("  " + p.replace(HOME, "~"))
        print(f"{'Would remove' if dry else 'Removed'} {removed} prompt(s) from ~/.claude/history.jsonl")
    if not dry:
        trash(paths)


def resolve(ids):
    known = set(all_transcripts()) | set(first_prompts())
    out = []
    for i in ids:
        hits = [s for s in known if s == i or (len(i) >= 8 and s.startswith(i))]
        if len(hits) != 1:
            sys.exit(f"'{i}': {'no session' if not hits else 'ambiguous, matches ' + ', '.join(hits)}")
        out.append(hits[0])
    return out


def cmd_list(args):
    show_all = "--all" in args
    n = int(args[args.index("-n") + 1]) if "-n" in args else 30
    me = os.environ.get("CLAUDE_CODE_SESSION_ID")
    running, prompts = running_sessions(), first_prompts()
    here = project_dir(os.getcwd())
    rows = [(os.path.getmtime(p), sid, p) for sid, p in all_transcripts().items()
            if show_all or os.path.dirname(p) == here]
    rows.sort(reverse=True)
    if not rows:
        print("No sessions" + ("" if show_all else f" for {os.getcwd()} (try --all)"))
    for mt, sid, p in rows[:n]:
        tag = " [THIS]" if sid == me else (" [RUNNING]" if sid in running else "")
        proj = os.path.basename(os.path.dirname(p)) if show_all else ""
        txt = " ".join((prompts.get(sid) or "").split())[:70]
        size = os.path.getsize(p) // 1024
        print(f"{time.strftime('%Y-%m-%d %H:%M', time.localtime(mt))}  {sid}  {size:>6}K{tag}  {proj}  {txt}")
    if len(rows) > n:
        print(f"... {len(rows) - n} more (use -n)")


def cmd_delete(args):
    dry = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]
    running = running_sessions()
    me = os.environ.get("CLAUDE_CODE_SESSION_ID")
    if "--older-than" in args:
        days = float(args[args.index("--older-than") + 1])
        cut = time.time() - days * 86400
        sids = [s for s, p in all_transcripts().items() if os.path.getmtime(p) < cut]
    else:
        sids = resolve(args)
    busy = [s for s in sids if s in running or s == me]
    for s in busy:
        print(f"skip {s}: still running" + (" (this session: use 'now')" if s == me else ""))
    sids = [s for s in sids if s not in busy]
    if not sids:
        sys.exit("Nothing to forget.")
    forget(sids, dry)


def cmd_now():
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID")
    pid = os.environ.get("CLAUDE_PID")
    if not sid or not pid:
        sys.exit("Run this from inside Claude Code (CLAUDE_CODE_SESSION_ID / CLAUDE_PID missing).")
    pid = int(pid)
    comm = subprocess.run(["ps", "-o", "comm=", "-p", str(pid)], capture_output=True, text=True).stdout.strip()
    if "claude" not in os.path.basename(comm).lower():
        sys.exit(f"PID {pid} is not Claude ({comm!r}); refusing.")
    log = open(os.devnull, "w")
    subprocess.Popen([sys.executable, "-I", os.path.abspath(__file__), "_after", str(pid), sid],
                     stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
    print(f"Closing Claude in 2s; session {sid} will then be moved to the Bin.")


def cmd_after(pid, sid):
    """Detached: close Claude, wait until it is gone, then clean everything."""
    time.sleep(2)
    for sig, wait in ((signal.SIGINT, 3), (signal.SIGTERM, 15), (signal.SIGKILL, 5)):
        if not alive(pid):
            break
        try:
            os.kill(pid, sig)
            if sig == signal.SIGINT:  # Claude asks for a second Ctrl+C to quit
                time.sleep(0.3)
                os.kill(pid, sig)
        except ProcessLookupError:
            break
        end = time.time() + wait
        while alive(pid) and time.time() < end:
            time.sleep(0.2)
    time.sleep(1)  # let final writes land before trashing them
    forget([sid], quiet=True)


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help", "help"):
        print(__doc__)
    elif a[0] == "now":
        cmd_now()
    elif a[0] == "list":
        cmd_list(a[1:])
    elif a[0] == "delete":
        cmd_delete(a[1:])
    elif a[0] == "_after":
        cmd_after(int(a[1]), a[2])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
