#!/usr/bin/env bash
# Read-only scanner for the `cleanup` skill. It never deletes or moves anything.
# Usage: scan.sh <overview|big|dupes|caches|stale|loose> [root]   (root defaults to $HOME)
set -u
MODE="${1:-overview}"
ROOT="${2:-$HOME}"
MIN_BIG_MB="${MIN_BIG_MB:-200}"     # threshold for "big" files
MIN_DUPE_MB="${MIN_DUPE_MB:-5}"     # ignore duplicates smaller than this
STALE_DAYS="${STALE_DAYS:-180}"     # "not touched in" threshold

# Never descend into these: secrets, system/app state, VCS internals, photo/music libraries.
PRUNE=( -name .Trash -o -name .ssh -o -name .gnupg -o -name Keychains -o -name .git
        -o -name node_modules -o -name '*.photoslibrary' -o -name '*.musiclibrary'
        -o -name '*.app' -o -path "$HOME/Library" -o -path "$HOME/.claude" -o -name .cache
        -o -name .npm -o -name .bun -o -name .cargo -o -name .rustup -o -name go )

hr() { awk '{ s=$1; u="B"; if(s>=1024){s/=1024;u="K"} if(s>=1024){s/=1024;u="M"} if(s>=1024){s/=1024;u="G"} $1=sprintf("%.1f%s",s,u); print }'; }

case "$MODE" in
overview)
  echo "## Disk"; df -h "$ROOT" | tail -1
  echo; echo "## Top-level folders in $ROOT (largest first)"
  du -sk "$ROOT"/* "$ROOT"/.[!.]* 2>/dev/null | sort -rn | head -30 | awk '{ $1=$1*1024; print }' | hr
  echo; echo "## Loose files directly in $ROOT"
  find "$ROOT" -maxdepth 1 -type f ! -name '.*' -exec stat -f '%z %Sm %N' -t '%Y-%m-%d' {} + 2>/dev/null | sort -rn | hr
  ;;
big)
  echo "## Files over ${MIN_BIG_MB}MB (size, last modified, last opened, path)"
  find "$ROOT" \( "${PRUNE[@]}" \) -prune -o -type f -size +"${MIN_BIG_MB}"M \
    -exec stat -f '%z %Sm %Sa %N' -t '%Y-%m-%d' {} + 2>/dev/null | sort -rn | head -60 | hr
  ;;
dupes)
  echo "## Duplicate files over ${MIN_DUPE_MB}MB (same size + same SHA-1). Groups separated by blank lines."
  TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
  find "$ROOT" \( "${PRUNE[@]}" \) -prune -o -type f -size +"${MIN_DUPE_MB}"M -print0 2>/dev/null \
    | xargs -0 stat -f '%z	%N' 2>/dev/null | sort -n > "$TMP/sizes"
  cut -f1 "$TMP/sizes" | uniq -d > "$TMP/dupsizes"
  grep -F -f <(sed 's/$/	/' "$TMP/dupsizes") "$TMP/sizes" | cut -f2- | while IFS= read -r f; do
    printf '%s\t%s\t%s\n' "$(shasum -a 1 "$f" 2>/dev/null | cut -d' ' -f1)" "$(stat -f %z "$f")" "$f"
  done | sort > "$TMP/hashed"
  cut -f1 "$TMP/hashed" | uniq -d | while read -r h; do
    grep "^$h	" "$TMP/hashed" | cut -f2- | awk -F'\t' '{ s=$1; printf "%.1fMB\t%s\n", s/1048576, $2 }'; echo
  done
  ;;
caches)
  echo "## Regenerable caches (safe to clear; apps/tools rebuild them)"
  for p in "$HOME/Library/Caches" "$HOME/.cache" "$HOME/.npm/_cacache" "$HOME/Library/pnpm/store" \
           "$HOME/.bun/install/cache" "$HOME/Library/Caches/ms-playwright" "$HOME/Library/Caches/Homebrew" \
           "$HOME/Library/Developer/Xcode/DerivedData" "$HOME/Library/Developer/Xcode/Archives" \
           "$HOME/Library/Developer/CoreSimulator/Caches" "$HOME/go/pkg/mod/cache" \
           "$HOME/Library/Caches/pip" "$HOME/.gradle/caches" "$HOME/Library/Logs" "$HOME/.Trash"; do
    [ -e "$p" ] && du -sk "$p" 2>/dev/null
  done | sort -rn | awk '{ $1=$1*1024; print }' | hr
  echo; echo "## Biggest entries inside ~/Library/Caches"
  du -sk "$HOME/Library/Caches"/* 2>/dev/null | sort -rn | head -15 | awk '{ $1=$1*1024; print }' | hr
  echo; echo "## node_modules / build output folders (size, project last modified, path)"
  find "$ROOT" \( -path "$HOME/Library" -o -name .git -o \( -path "$HOME/.?*" -a ! -path "$HOME/.*/*" \) \) -prune -o \
    -type d \( -name node_modules -o -name .next -o -name dist -o -name .astro -o -name .vercel -o -name target -o -name .turbo \) -prune -print 2>/dev/null \
    | while IFS= read -r d; do printf '%s %s %s\n' "$(du -sk "$d" 2>/dev/null | cut -f1)" "$(stat -f %Sm -t %Y-%m-%d "$(dirname "$d")")" "$d"; done \
    | sort -rn | head -40 | awk '{ $1=$1*1024; print }' | hr
  ;;
stale)
  echo "## Files over 50MB not opened in ${STALE_DAYS} days (installers, archives, videos...)"
  find "$ROOT" \( "${PRUNE[@]}" \) -prune -o -type f -size +50M -atime +"$STALE_DAYS" \
    -exec stat -f '%z %Sa %N' -t '%Y-%m-%d' {} + 2>/dev/null | sort -rn | head -50 | hr
  echo; echo "## Installers and archives in Downloads/Desktop/home (often already used)"
  find "$HOME/Downloads" "$HOME/Desktop" "$HOME" -maxdepth 2 -type f \
    \( -iname '*.dmg' -o -iname '*.pkg' -o -iname '*.zip' -o -iname '*.iso' -o -iname '*.tar.gz' -o -iname '*.rar' -o -iname '*.7z' \) \
    -exec stat -f '%z %Sm %N' -t '%Y-%m-%d' {} + 2>/dev/null | sort -rn | uniq | head -40 | hr
  ;;
loose)
  echo "## File types in Desktop, Downloads, Documents and home root (for grouping)"
  for d in "$HOME" "$HOME/Desktop" "$HOME/Downloads" "$HOME/Documents"; do
    echo "### $d"
    find "$d" -maxdepth 1 -type f ! -name '.*' 2>/dev/null \
      | awk '{ n=split($0,p,"/"); f=p[n]; i=match(f,/\.[A-Za-z0-9]+$/); print (i ? tolower(substr(f,i+1)) : "(no ext)") }' \
      | sort | uniq -c | sort -rn | head -15
    echo "  folders: $(find "$d" -mindepth 1 -maxdepth 1 -type d ! -name '.*' 2>/dev/null | wc -l | tr -d ' ')"
  done
  echo; echo "## Code projects outside ~/Code (git repos or package.json at depth <=3)"
  find "$HOME" -maxdepth 3 \( -name .git -o -name package.json \) -print -o \
    \( -path "$HOME/Library" -o -path "$HOME/Code" -o -name node_modules -o -name '.?*' \) -prune 2>/dev/null \
    | while IFS= read -r p; do dirname "$p"; done | sort -u
  ;;
*) echo "unknown mode: $MODE (overview|big|dupes|caches|stale|loose)"; exit 2 ;;
esac
