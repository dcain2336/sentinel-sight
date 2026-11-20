#!/usr/bin/env bash
# push-clean check: fail loudly if any GRID data file or the GRID starter
# directory is tracked in git. Run before every push.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)" || exit 1
if git ls-files | grep -Ei '\.(zst|jsonl|parquet|sqlite|duckdb)$|stl-hackathon-2026-grid-starter' ; then
  echo "ERROR: push-clean check FAILED — GRID data file(s) tracked in git. Remove them before pushing." >&2
  exit 1
fi
echo "OK: push-clean check passed — no GRID data files tracked."
