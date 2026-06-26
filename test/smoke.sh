#!/usr/bin/env bash
#
# Smoke test for the habits CLI. Exercises every subcommand against a throwaway
# XDG data dir so it never touches your real habit storage. Exits non-zero if
# any check fails.
#
# Usage:
#   test/smoke.sh                 # tests ./dist/habits (run `make` first)
#   HABITS_BIN=~/.local/bin/habits test/smoke.sh   # test an installed copy
#
set -euo pipefail

HABITS_BIN="${HABITS_BIN:-dist/habits}"

if [ ! -x "$HABITS_BIN" ]; then
  echo "error: '$HABITS_BIN' not found or not executable. Run 'make' first," \
       "or set HABITS_BIN." >&2
  exit 1
fi

# Isolate all state in a temp XDG tree; never the user's real ~/.local/share.
WORK="$(mktemp -d)"
export XDG_DATA_HOME="$WORK/data"
export XDG_CONFIG_HOME="$WORK/config"
trap 'rm -rf "$WORK"' EXIT

PASS=0
FAIL=0
OUT=""
RC=0

# run habits with the given args, capturing combined output in OUT and exit
# status in RC without tripping set -e.
run() {
  OUT="$("$HABITS_BIN" "$@" 2>&1)" && RC=0 || RC=$?
}

# run habits feeding the first argument to stdin (for the y/n delete prompt).
run_in() {
  local input="$1"
  shift
  OUT="$(printf '%s\n' "$input" | "$HABITS_BIN" "$@" 2>&1)" && RC=0 || RC=$?
}

pass() { PASS=$((PASS + 1)); printf '  ok   %s\n' "$1"; }
fail() { FAIL=$((FAIL + 1)); printf '  FAIL %s\n' "$1"; printf '%s\n' "$OUT" | sed 's/^/         | /'; }

ok()      { if [ "$RC" -eq 0 ]; then pass "$1"; else fail "$1 (exit $RC)"; fi; }
not_ok()  { if [ "$RC" -ne 0 ]; then pass "$1"; else fail "$1 (expected non-zero exit)"; fi; }
has()     { case "$OUT" in *"$1"*) pass "$2";; *) fail "$2 (missing text: $1)";; esac; }
hasnt()   { case "$OUT" in *"$1"*) fail "$2 (unexpected text: $1)";; *) pass "$2";; esac; }

echo "habits smoke test ($HABITS_BIN)"

run -h
ok "help exits cleanly"
has "usage: habits" "help shows usage with prog name"

run -l
ok "list on empty store"

run -n alpha
ok "create new habit"
has "created" "create reports success"

run
ok "bare invocation lists habits"
has "alpha" "new habit appears in list"

run -c 1 alpha
ok "complete habit"
has "completed" "complete reports success"

run -s
ok "stats"
has "alpha" "stats include the habit"

run -a
ok "list all (current)"
has "alpha" "habit shows under current"

run -r alpha
ok "archive habit"
has "archived" "archive reports success"

run -l
hasnt "alpha" "archived habit gone from current list"

run -a
has "alpha" "archived habit shows under archived"

run -u alpha
ok "un-archive habit"
has "un-archived" "un-archive reports success"

run -l
has "alpha" "un-archived habit back in current list"

# error paths
run -c
not_ok "missing value for -c is rejected"

run -r
not_ok "missing habit positional is rejected"

# delete: cancel then confirm
run_in n -d alpha
ok "delete prompt accepts 'n'"
has "Canceling" "declining keeps the habit"

run -l
has "alpha" "habit still present after declined delete"

run_in y -d alpha
ok "delete prompt accepts 'y'"
has "deleted" "confirming removes the habit"

run -l
hasnt "alpha" "habit gone after confirmed delete"

echo
echo "passed: $PASS  failed: $FAIL"
[ "$FAIL" -eq 0 ]
